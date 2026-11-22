"""Textos apresentados ao aluno, iguais no terminal e no Telegram."""

from datetime import time

from guia_salas.dados import RegistroDeAtualizacao
from guia_salas.dominio import DiaSemana, GradeDoAluno, Sala, Turma
from guia_salas.servicos.atualizador import RelatorioDeAtualizacao
from guia_salas.servicos.consulta import ResultadoDaBusca
from guia_salas.servicos.planilha import ResultadoDaPlanilha

LIMITE_DA_MENSAGEM = 4000

MENSAGEM_DE_AJUDA = (
    "Comandos do Guia de Salas (ICEx):\n"
    "/sala <nome ou código>: turmas, dias, horários e salas da disciplina\n"
    "   ex.: /sala banco de dados   ou   /sala DCC011\n"
    "/livres <dia> <hora> [andar] [prédio]: salas sem aula\n"
    "   ex.: /livres ter 14:00 1   ou   /livres seg 10:00 cad3\n"
    "/minhagrade: mostra as turmas salvas\n"
    "/adicionar <código> <turma>; ...: salva turmas na grade\n"
    "   ex.: /adicionar DCC011 TB; MAT001 TA1\n"
    "/remover <código>: retira a disciplina da grade\n"
    "Envie uma planilha .xlsx com suas disciplinas na primeira coluna "
    "para receber a grade com as salas."
)


class FormatadorDeRespostas:
    """Transforma resultados das consultas e operações em mensagens de texto."""

    def busca(self, resultado: ResultadoDaBusca) -> str:
        """Turmas e aulas encontradas, ou o aviso de que nada foi encontrado."""
        if not resultado.encontrou:
            return (f"Nenhuma disciplina encontrada para \"{resultado.termo}\".\n"
                    "Tente pelo código, como DCC011.")
        blocos = []
        for disciplina in resultado.disciplinas:
            linhas = [f"{disciplina.codigo} - {disciplina.nome}"]
            linhas += [self.turma(turma) for turma in disciplina.turmas]
            blocos.append("\n".join(linhas))
        return "\n\n".join(blocos)

    def turma(self, turma: Turma) -> str:
        """Uma linha por turma, juntando os dias que têm o mesmo horário e sala."""
        grupos: dict[tuple, list[str]] = {}
        for aula in turma.aulas:
            grupos.setdefault((aula.intervalo, aula.sala), []).append(aula.dia.sigla.capitalize())
        partes = [f"{'/'.join(dias)} {intervalo}, {sala.descricao()}"
                  for (intervalo, sala), dias in grupos.items()]
        return f"  {turma.codigo}: " + "; ".join(partes)

    def termo_invalido(self, motivo: str) -> str:
        """Mensagem para um termo de busca rejeitado."""
        return f"{motivo}\nExemplo: /sala banco de dados"

    def salas_livres(self, salas: list[Sala], dia: DiaSemana, instante: time,
                     andar: int | None) -> str:
        """Lista de salas livres, ou aviso explícito de que nenhuma está livre."""
        onde = f" no {andar}º andar" if andar is not None else ""
        quando = f"{dia.nome}, {instante:%H:%M}"
        if not salas:
            return f"Nenhuma sala livre{onde} ({quando})."
        nomes = "\n".join(f"  {s.identificador} ({s.predio})" for s in salas)
        return f"Salas livres{onde} ({quando}):\n{nomes}"

    def planilha(self, resultado: ResultadoDaPlanilha) -> str:
        """Totais do preenchimento da planilha."""
        return (f"{resultado.localizadas} disciplina(s) localizada(s), "
                f"{resultado.nao_localizadas} não localizada(s).")

    def grade(self, grade: GradeDoAluno) -> str:
        """Aulas da grade em ordem de dia e horário, e as disciplinas que saíram da base."""
        cabecalho = f"Grade: {grade.nome} ({grade.quantidade} disciplina(s))"
        if grade.quantidade == 0:
            return f"{cabecalho}\nA grade está vazia. Exemplo: /adicionar DCC011 TB"
        linhas = [cabecalho]
        dia_atual = None
        for aula in grade.aulas():
            if aula.dia != dia_atual:
                dia_atual = aula.dia
                linhas.append(f"{aula.dia.nome}:")
            linhas.append(f"  {aula.intervalo} {aula.disciplina.codigo} {aula.turma.codigo}, "
                          f"{aula.sala.descricao()}")
        if grade.ausentes:
            ausentes = ", ".join(f"{c} {t}" for c, t in grade.ausentes.items())
            linhas.append(f"Não encontradas na base atual: {ausentes}")
        return "\n".join(linhas)

    def turmas_adicionadas(self, turmas: list[Turma]) -> str:
        """Confirmação da inclusão na grade."""
        nomes = ", ".join(f"{t.disciplina.codigo} {t.codigo}" for t in turmas)
        return f"Adicionada(s) à grade: {nomes}."

    def disciplina_removida(self, codigo: str) -> str:
        """Confirmação da remoção da grade."""
        return f"{codigo} removida da grade."

    def atualizacao(self, relatorio: RelatorioDeAtualizacao) -> str:
        """Resumo de uma atualização aceita."""
        return (f"Base atualizada: {relatorio.registros_lidos} registros lidos, "
                f"{relatorio.aulas_registradas} aulas registradas, "
                f"{len(relatorio.recusados)} registros recusados.")

    def situacao_da_base(self, disciplinas: int, aulas: int,
                         ultima: RegistroDeAtualizacao | None) -> str:
        """Linha de abertura com o tamanho da base e a última atualização."""
        texto = f"Base: {disciplinas} disciplinas, {aulas} aulas."
        if ultima:
            texto += f" Última atualização: {ultima.momento}, {ultima.origem}."
        return texto


def dividir_mensagem(texto: str, limite: int = LIMITE_DA_MENSAGEM) -> list[str]:
    """Divide um texto longo em partes que cabem numa mensagem do Telegram, quebrando entre linhas."""
    partes, atual = [], ""
    for linha in texto.splitlines(keepends=True):
        if atual and len(atual) + len(linha) > limite:
            partes.append(atual.rstrip("\n"))
            atual = ""
        atual += linha
    if atual:
        partes.append(atual.rstrip("\n"))
    return partes or [""]
