"""Sala de aula."""

from datetime import time
from typing import TYPE_CHECKING, Iterable

from guia_salas.dominio.erros import DadoInvalido

if TYPE_CHECKING:
    from guia_salas.dominio.aula import Aula
    from guia_salas.dominio.dia_semana import DiaSemana


class Sala:
    """Espaço físico onde aulas acontecem, identificado dentro de um prédio."""

    def __init__(self, identificador: str, predio: str, andar: int | None):
        """Valida identificador e prédio não vazios e andar não negativo (None quando desconhecido)."""
        identificador = identificador.strip()
        predio = predio.strip()
        if not identificador:
            raise DadoInvalido("A sala precisa de um identificador.")
        if not predio:
            raise DadoInvalido("A sala precisa de um prédio.")
        if andar is not None and andar < 0:
            raise DadoInvalido("O andar não pode ser negativo.")
        self._identificador = identificador
        self._predio = predio
        self._andar = andar

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

    @property
    def presencial(self) -> bool:
        """Indica se é um espaço físico (aulas on-line não ocupam sala)."""
        return self._predio.lower() != "on-line"

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

    def __eq__(self, outra: object) -> bool:
        return isinstance(outra, Sala) and self.chave == outra.chave

    def __hash__(self) -> int:
        return hash(self.chave)

    def __str__(self) -> str:
        if not self.presencial:
            return "On-line"
        andar = f", {self._andar}º andar" if self._andar is not None else ""
        return f"Sala {self._identificador} ({self._predio}{andar})"

    def __repr__(self) -> str:
        return f"Sala({self._identificador!r}, {self._predio!r}, {self._andar})"
