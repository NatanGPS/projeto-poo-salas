"""Menu de terminal do protótipo."""

from typing import Callable

from guia_salas.bot.formatacao import FormatadorDeRespostas
from guia_salas.dominio import DadoInvalido, DiaSemana, ErroDeDominio
from guia_salas.dominio.intervalo import ler_hora
from guia_salas.servicos.consulta import ConsultaDeSalas

OPCOES = (
    "1 - Buscar a sala de uma disciplina",
    "2 - Consultar salas livres",
    "0 - Sair",
)


class MenuTerminal:
    """Menu de texto com as funcionalidades F01 e F02."""

    def __init__(self, consulta: ConsultaDeSalas, descricao_base: str,
                 ler: Callable[[str], str] = input, escrever: Callable[[str], None] = print,
                 formatador: FormatadorDeRespostas | None = None):
        """Recebe a consulta, um resumo da base e as funções de leitura e escrita."""
        self._consulta = consulta
        self._descricao_base = descricao_base
        self._ler = ler
        self._escrever = escrever
        self._formatador = formatador or FormatadorDeRespostas()

    def executar(self) -> None:
        """Mostra o menu até o usuário escolher sair."""
        self._escrever("=== Guia de Salas (ICEx) ===")
        self._escrever(self._descricao_base)
        while True:
            self._escrever("\n" + "\n".join(OPCOES))
            try:
                opcao = self._ler("Opção: ").strip()
            except EOFError:
                break
            if opcao == "0":
                break
            acoes = {"1": self.buscar_disciplina, "2": self.consultar_salas_livres}
            acao = acoes.get(opcao)
            if acao is None:
                self._escrever("Opção inválida. Digite 1, 2 ou 0.")
                continue
            try:
                acao()
            except EOFError:
                break
        self._escrever("Encerrado.")

    def buscar_disciplina(self) -> None:
        """F01: pede o nome ou código e mostra as turmas, dias, horários e salas."""
        termo = self._ler("Nome ou código da disciplina: ")
        try:
            resultado = self._consulta.buscar_por_disciplina(termo)
        except ErroDeDominio as erro:
            self._escrever(f"Entrada recusada: {erro}")
            return
        self._escrever(self._formatador.busca(resultado))

    def consultar_salas_livres(self) -> None:
        """F02: pede dia, hora, andar e prédio e mostra as salas sem aula naquele instante."""
        try:
            dia = DiaSemana.de_texto(self._ler("Dia (seg, ter, qua, qui, sex, sab): "))
            instante = ler_hora(self._ler("Hora (HH:MM): "))
            andar = self._ler_andar(self._ler("Andar (vazio para todos): "))
            predio = self._ler(f"Prédio ({', '.join(self._consulta.catalogo.predios)}, vazio para todos): ").strip()
            salas = self._consulta.salas_livres(dia, instante, andar, predio or None)
        except ErroDeDominio as erro:
            self._escrever(f"Entrada recusada: {erro}")
            return
        self._escrever(self._formatador.salas_livres(salas, dia, instante, andar))

    @staticmethod
    def _ler_andar(texto: str) -> int | None:
        """Converte o andar digitado; vazio significa todos os andares."""
        texto = texto.strip()
        if not texto:
            return None
        try:
            return int(texto)
        except ValueError as erro:
            raise DadoInvalido(f"Andar inválido: \"{texto}\". Use um número, como 2.") from erro
