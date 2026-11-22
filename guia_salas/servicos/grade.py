"""Preenchimento da grade enviada pelo aluno."""

from pathlib import Path

from openpyxl import load_workbook

from guia_salas.dominio import TermoDeBuscaInvalido
from guia_salas.servicos.consulta import ConsultaDeSalas

NAO_LOCALIZADA = "não localizada"
COLUNAS_ACRESCENTADAS = ("Turma encontrada", "Dias e horários", "Sala")


class PreenchedorDeGrade:
    """Completa uma planilha de disciplinas com turma, horários e sala."""

    def __init__(self, consulta: ConsultaDeSalas):
        """Recebe a consulta usada para localizar cada disciplina."""
        self._consulta = consulta

    def preencher(self, entrada: Path, saida: Path) -> tuple[int, int]:
        """Preenche a planilha e devolve (localizadas, não localizadas)."""
        livro = load_workbook(entrada)
        folha = livro.active
        titulos = [str(c.value or "").strip().lower() for c in folha[1]]
        coluna_turma = titulos.index("turma") + 1 if "turma" in titulos else None
        primeira_nova = folha.max_column + 1
        for deslocamento, titulo in enumerate(COLUNAS_ACRESCENTADAS):
            folha.cell(row=1, column=primeira_nova + deslocamento, value=titulo)

        localizadas = nao_localizadas = 0
        for linha in range(2, folha.max_row + 1):
            termo = str(folha.cell(row=linha, column=1).value or "").strip()
            if not termo:
                continue
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
        livro.save(saida)
        return localizadas, nao_localizadas

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
