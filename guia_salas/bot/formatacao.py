"""Textos apresentados ao aluno."""

from datetime import time

from guia_salas.dominio import DiaSemana, Sala, Turma
from guia_salas.servicos.consulta import ResultadoDaBusca

LIMITE_DA_MENSAGEM = 4000

MENSAGEM_DE_AJUDA = (
    "Comandos do Guia de Salas (ICEx):\n"
    "/sala <nome ou código>: turmas, dias, horários e salas da disciplina\n"
    "   ex.: /sala banco de dados   ou   /sala DCC011\n"
    "/livres <dia> <hora> <andar> [prédio]: salas sem aula\n"
    "   ex.: /livres ter 14:00 1   ou   /livres seg 10:00 3 cad3\n"
    "Envie uma planilha .xlsx com suas disciplinas na primeira coluna "
    "para receber a grade com as salas."
)


class FormatadorDeRespostas:
    """Transforma resultados das consultas em mensagens de texto."""

    def busca(self, resultado: ResultadoDaBusca) -> str:
        """Mensagem com as turmas e aulas encontradas, ou o aviso de que nada foi encontrado."""
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
        partes = [f"{'/'.join(dias)} {intervalo}, {self.local(sala)}"
                  for (intervalo, sala), dias in grupos.items()]
        return f"  {turma.codigo}: " + "; ".join(partes)

    def local(self, sala: Sala) -> str:
        """Descrição curta da sala, com prédio e andar quando conhecidos."""
        if not sala.presencial:
            return "on-line"
        andar = f", {sala.andar}º andar" if sala.andar is not None else ""
        return f"sala {sala.identificador} ({sala.predio}{andar})"

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
