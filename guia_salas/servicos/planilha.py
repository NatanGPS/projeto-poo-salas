"""F03: preenchimento da planilha de disciplinas enviada pelo aluno."""

import zipfile
from dataclasses import dataclass
from pathlib import Path

from guia_salas.dominio import PlanilhaInvalida, TermoDeBuscaInvalido
from guia_salas.servicos.consulta import ConsultaDeSalas

NAO_LOCALIZADA = "não localizada"
COLUNAS_ACRESCENTADAS = ("Turma encontrada", "Dias e horários", "Sala")


@dataclass(frozen=True)
class ResultadoDaPlanilha:
    """Totais do preenchimento e caminho da planilha gerada."""

    localizadas: int
    nao_localizadas: int
    saida: Path


class PreenchedorDeGrade:
    """Gera uma cópia da planilha com turma, horários e sala de cada disciplina da primeira coluna."""

    def __init__(self, consulta: ConsultaDeSalas):
        """Recebe a consulta usada para localizar cada disciplina."""
        self._consulta = consulta

    @staticmethod
    def caminho_de_saida(entrada: Path | str) -> Path:
        """Nome da planilha gerada: o da entrada com o sufixo _com_salas."""
        entrada = Path(entrada)
        return entrada.with_name(f"{entrada.stem}_com_salas.xlsx")

    def preencher(self, entrada: Path | str, saida: Path | str | None = None) -> ResultadoDaPlanilha:
        """Lê a entrada (.xlsx), grava a cópia preenchida em saida e devolve os totais; a entrada não muda."""
        entrada = Path(entrada)
        saida = Path(saida) if saida else self.caminho_de_saida(entrada)
        if entrada.suffix.lower() != ".xlsx":
            raise PlanilhaInvalida("Envie uma planilha no formato .xlsx.")
        if not entrada.is_file():
            raise PlanilhaInvalida(f"Arquivo não encontrado: {entrada}.")
        if saida.resolve() == entrada.resolve():
            raise PlanilhaInvalida("A planilha gerada não pode substituir a original.")
        try:
            from openpyxl import load_workbook
            from openpyxl.utils.exceptions import InvalidFileException
        except ImportError as erro:
            raise PlanilhaInvalida("Instale a biblioteca openpyxl (pip install -r requirements.txt).") from erro
        try:
            livro = load_workbook(entrada)
        except (OSError, KeyError, ValueError, zipfile.BadZipFile, InvalidFileException) as erro:
            raise PlanilhaInvalida("Não foi possível abrir o arquivo como planilha .xlsx.") from erro
        folha = livro.active
        linhas = [n for n in range(2, folha.max_row + 1)
                  if str(folha.cell(row=n, column=1).value or "").strip()]
        if not linhas:
            raise PlanilhaInvalida("A planilha não tem disciplinas na primeira coluna (a linha 1 é o cabeçalho).")

        titulos = [str(c.value or "").strip().lower() for c in folha[1]]
        coluna_turma = titulos.index("turma") + 1 if "turma" in titulos else None
        primeira_nova = folha.max_column + 1
        for deslocamento, titulo in enumerate(COLUNAS_ACRESCENTADAS):
            folha.cell(row=1, column=primeira_nova + deslocamento, value=titulo)

        localizadas = nao_localizadas = 0
        for linha in linhas:
            termo = str(folha.cell(row=linha, column=1).value).strip()
            turma_pedida = (str(folha.cell(row=linha, column=coluna_turma).value or "").strip().upper()
                            if coluna_turma else "")
            valores = self._valores_para(termo, turma_pedida)
            if valores is None:
                nao_localizadas += 1
                valores = (NAO_LOCALIZADA, "", "")
            else:
                localizadas += 1
            for deslocamento, valor in enumerate(valores):
                folha.cell(row=linha, column=primeira_nova + deslocamento, value=valor)
        try:
            livro.save(saida)
        except OSError as erro:
            raise PlanilhaInvalida(f"Não foi possível gravar {saida}: {erro.strerror}.") from erro
        return ResultadoDaPlanilha(localizadas, nao_localizadas, saida)

    def _valores_para(self, termo: str, turma_pedida: str) -> tuple[str, str, str] | None:
        """Turma, horários e salas da primeira disciplina encontrada, ou None."""
        try:
            resultado = self._consulta.buscar_por_disciplina(termo)
        except TermoDeBuscaInvalido:
            return None
        if not resultado.encontrou:
            return None
        turmas = resultado.disciplinas[0].turmas
        if turma_pedida:
            turmas = [t for t in turmas if t.codigo == turma_pedida]
        if not turmas:
            return None
        turma = turmas[0]
        horarios = "; ".join(f"{a.dia.sigla} {a.intervalo}" for a in turma.aulas)
        salas = ", ".join(dict.fromkeys(f"{a.sala.identificador} ({a.sala.predio})" for a in turma.aulas))
        return turma.codigo, horarios, salas
