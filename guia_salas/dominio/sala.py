"""Salas de aula: a sala física e a sala virtual das aulas on-line."""

from datetime import time
from typing import TYPE_CHECKING, Iterable

from guia_salas.dominio.erros import DadoInvalido

if TYPE_CHECKING:
    from guia_salas.dominio.aula import Aula
    from guia_salas.dominio.dia_semana import DiaSemana

PREDIO_ONLINE = "On-line"


class Sala:
    """Espaço físico onde aulas acontecem, identificado pelo par (prédio, identificador)."""

    def __init__(self, identificador: str, predio: str, andar: int | None):
        """Valida identificador e prédio não vazios; o andar passa pelo setter."""
        identificador = identificador.strip()
        predio = predio.strip()
        if not identificador:
            raise DadoInvalido("A sala precisa de um identificador.")
        if not predio:
            raise DadoInvalido("A sala precisa de um prédio.")
        self._identificador = identificador
        self._predio = predio
        self._andar: int | None = None
        self.andar = andar

    @classmethod
    def criar(cls, identificador: str, predio: str, andar: int | None) -> "Sala":
        """Cria uma SalaOnline para o prédio On-line e uma Sala nos demais casos."""
        if predio.strip().casefold() == PREDIO_ONLINE.casefold():
            return SalaOnline(identificador)
        return Sala(identificador, predio, andar)

    @property
    def identificador(self) -> str:
        """Nome da sala dentro do prédio, como 1024 ou 2014 - DCC."""
        return self._identificador

    @property
    def predio(self) -> str:
        """Prédio da sala: ICEx, CAD1, CAD2, CAD3 ou On-line."""
        return self._predio

    @property
    def andar(self) -> int | None:
        """Número do andar, ou None quando não é possível saber."""
        return self._andar

    @andar.setter
    def andar(self, valor: int | None) -> None:
        """Aceita None (andar desconhecido) ou um inteiro não negativo."""
        if valor is not None and (isinstance(valor, bool) or not isinstance(valor, int)):
            raise DadoInvalido(f"Andar inválido: {valor!r}.")
        if valor is not None and valor < 0:
            raise DadoInvalido("O andar não pode ser negativo.")
        self._andar = valor

    @property
    def presencial(self) -> bool:
        """Indica se é um espaço físico, que pode estar livre ou ocupado."""
        return True

    @property
    def chave(self) -> tuple[str, str]:
        """Par (prédio, identificador), sem diferenciar maiúsculas, que identifica a sala."""
        return (self._predio.casefold(), self._identificador.casefold())

    def esta_livre(self, dia: "DiaSemana", instante: time, aulas: Iterable["Aula"]) -> bool:
        """Indica se nenhuma das aulas informadas ocupa esta sala no dia e instante."""
        return not any(
            aula.sala == self and aula.dia == dia and aula.intervalo.contem(instante)
            for aula in aulas
        )

    def descricao(self) -> str:
        """Texto curto usado nas respostas, como sala 213 (CAD3, 2º andar)."""
        andar = f", {self._andar}º andar" if self._andar is not None else ""
        return f"sala {self._identificador} ({self._predio}{andar})"

    def __eq__(self, outra: object) -> bool:
        return isinstance(outra, Sala) and self.chave == outra.chave

    def __hash__(self) -> int:
        return hash(self.chave)

    def __str__(self) -> str:
        return self.descricao()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._identificador!r}, {self._predio!r}, {self._andar})"


class SalaOnline(Sala):
    """Sala virtual das aulas remotas: não tem andar e nunca aparece como livre."""

    def __init__(self, identificador: str = "ON-LINE"):
        """Cria a sala no prédio On-line, sem andar."""
        super().__init__(identificador, PREDIO_ONLINE, None)

    @property
    def andar(self) -> None:
        """Aulas on-line não têm andar."""
        return None

    @andar.setter
    def andar(self, valor: int | None) -> None:
        """Só aceita None, pois a sala não existe fisicamente."""
        if valor is not None:
            raise DadoInvalido("Uma sala on-line não tem andar.")

    @property
    def presencial(self) -> bool:
        """Aula on-line não ocupa espaço físico."""
        return False

    def esta_livre(self, dia: "DiaSemana", instante: time, aulas: Iterable["Aula"]) -> bool:
        """Nunca é oferecida como sala livre."""
        return False

    def descricao(self) -> str:
        """Texto curto usado nas respostas."""
        return "on-line"
