"""Comandos do bot, independentes do Telegram."""

from datetime import time

from guia_salas.bot.formatacao import MENSAGEM_DE_AJUDA, FormatadorDeRespostas
from guia_salas.dominio import DadoInvalido, DiaSemana, ErroDeDominio, TermoDeBuscaInvalido
from guia_salas.servicos.consulta import ConsultaDeSalas


class ComandosDoBot:
    """Recebe o texto de cada comando e devolve a mensagem de resposta."""

    def __init__(self, consulta: ConsultaDeSalas, formatador: FormatadorDeRespostas | None = None):
        self._consulta = consulta
        self._formatador = formatador or FormatadorDeRespostas()

    def ajuda(self) -> str:
        """Mensagem com os comandos disponíveis."""
        return MENSAGEM_DE_AJUDA

    def sala(self, termo: str) -> str:
        """Responde ao comando /sala com as aulas da disciplina buscada."""
        try:
            resultado = self._consulta.buscar_por_disciplina(termo)
        except TermoDeBuscaInvalido as erro:
            return self._formatador.termo_invalido(str(erro))
        return self._formatador.busca(resultado)

    def livres(self, argumentos: str) -> str:
        """Responde ao comando /livres <dia> <hora> <andar> [prédio]."""
        partes = argumentos.split()
        if len(partes) < 3:
            return "Uso: /livres <dia> <hora> <andar> [prédio]\nExemplo: /livres ter 14:00 1"
        try:
            dia = DiaSemana.de_texto(partes[0])
            horas, _, minutos = partes[1].lower().replace("h", ":").partition(":")
            instante = time(int(horas), int(minutos or 0))
            andar = int(partes[2])
        except (DadoInvalido, ValueError):
            return "Dia, hora ou andar inválido.\nExemplo: /livres ter 14:00 1"
        predio = " ".join(partes[3:]) or None
        try:
            salas = self._consulta.salas_livres(dia, instante, andar, predio)
        except ErroDeDominio as erro:
            return str(erro)
        return self._formatador.salas_livres(salas, dia, instante, andar)
