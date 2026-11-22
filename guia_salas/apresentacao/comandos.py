"""Comandos do bot, independentes do Telegram: recebem texto e devolvem texto."""

from guia_salas.apresentacao.formatacao import MENSAGEM_DE_AJUDA, FormatadorDeRespostas
from guia_salas.dominio import DiaSemana, ErroDeDominio, TermoDeBuscaInvalido, ler_hora
from guia_salas.sistema import Sistema

USO_LIVRES = "Uso: /livres <dia> <hora> [andar] [prédio]\nExemplo: /livres ter 14:00 1"
NOME_DA_GRADE_NO_TELEGRAM = "Minha grade"


class ComandosDoBot:
    """Traduz o texto de cada comando em chamadas aos serviços e devolve a resposta."""

    def __init__(self, sistema: Sistema, formatador: FormatadorDeRespostas | None = None):
        """Recebe o sistema montado e, opcionalmente, o formatador."""
        self._sistema = sistema
        self._formatador = formatador or FormatadorDeRespostas()

    @staticmethod
    def aluno_do_chat(id_do_chat: int) -> str:
        """Identificador da grade de uma conversa do Telegram."""
        return f"telegram:{id_do_chat}"

    def ajuda(self) -> str:
        """Mensagem com os comandos disponíveis."""
        return MENSAGEM_DE_AJUDA

    def sala(self, termo: str) -> str:
        """F01: /sala <nome ou código>."""
        try:
            resultado = self._sistema.consulta.buscar_por_disciplina(termo)
        except TermoDeBuscaInvalido as erro:
            return self._formatador.termo_invalido(str(erro))
        return self._formatador.busca(resultado)

    def livres(self, argumentos: str) -> str:
        """F02: /livres <dia> <hora> [andar] [prédio]; sem andar, considera todos."""
        partes = argumentos.split()
        if len(partes) < 2:
            return USO_LIVRES
        try:
            dia = DiaSemana.de_texto(partes[0])
            instante = ler_hora(partes[1])
            resto = partes[2:]
            andar = None
            if resto and resto[0].lstrip("-").isdigit():
                andar = int(resto.pop(0))
            predio = " ".join(resto) or None
            salas = self._sistema.consulta.salas_livres(dia, instante, andar, predio)
        except ErroDeDominio as erro:
            return f"{erro}\n{USO_LIVRES}"
        return self._formatador.salas_livres(salas, dia, instante, andar)

    def minha_grade(self, aluno: str) -> str:
        """F05: /minhagrade."""
        try:
            grade = self._sistema.minha_grade.abrir(aluno, NOME_DA_GRADE_NO_TELEGRAM)
        except ErroDeDominio as erro:
            return str(erro)
        return self._formatador.grade(grade)

    def adicionar(self, aluno: str, argumentos: str) -> str:
        """F05: /adicionar DCC011 TB; MAT001 TA1."""
        try:
            turmas = self._sistema.minha_grade.adicionar(aluno, argumentos, NOME_DA_GRADE_NO_TELEGRAM)
        except ErroDeDominio as erro:
            return f"Nada foi alterado. {erro}"
        return self._formatador.turmas_adicionadas(turmas)

    def remover(self, aluno: str, argumentos: str) -> str:
        """F05: /remover DCC011."""
        if not argumentos.strip():
            return "Uso: /remover <código da disciplina>\nExemplo: /remover DCC011"
        try:
            codigo = self._sistema.minha_grade.remover(aluno, argumentos)
        except ErroDeDominio as erro:
            return f"Nada foi alterado. {erro}"
        return self._formatador.disciplina_removida(codigo)

    def planilha(self, entrada, saida) -> str:
        """F03: preenche a planilha recebida e devolve a legenda; recusas chegam como ErroDeDominio."""
        return self._formatador.planilha(self._sistema.planilha.preencher(entrada, saida))
