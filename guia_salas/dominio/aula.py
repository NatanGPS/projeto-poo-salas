"""Encontro semanal de uma turma."""

from typing import TYPE_CHECKING

from guia_salas.dominio.dia_semana import DiaSemana
from guia_salas.dominio.intervalo import IntervaloDeHorario
from guia_salas.dominio.sala import Sala

if TYPE_CHECKING:
    from guia_salas.dominio.disciplina import Disciplina
    from guia_salas.dominio.turma import Turma


class Aula:
    """Aula semanal de uma turma, em um dia, horário e sala."""

    def __init__(self, turma: "Turma", dia: DiaSemana, intervalo: IntervaloDeHorario,
                 sala: Sala, origem: str):
        """Cria a aula; deve ser chamado por Turma.agendar_aula, que verifica as regras."""
        self._turma = turma
        self._dia = dia
        self._intervalo = intervalo
        self._sala = sala
        self._origem = origem

    @property
    def turma(self) -> "Turma":
        """Turma à qual a aula pertence."""
        return self._turma

    @property
    def disciplina(self) -> "Disciplina":
        """Disciplina da turma."""
        return self._turma.disciplina

    @property
    def dia(self) -> DiaSemana:
        """Dia da semana da aula."""
        return self._dia

    @property
    def intervalo(self) -> IntervaloDeHorario:
        """Horário de início e fim."""
        return self._intervalo

    @property
    def sala(self) -> Sala:
        """Sala onde a aula acontece."""
        return self._sala

    @property
    def origem(self) -> str:
        """Nome da fonte de dados de onde a aula foi obtida."""
        return self._origem

    def mesmo_encontro(self, outra: "Aula") -> bool:
        """Indica se as duas aulas descrevem o mesmo encontro (turma, dia, horário e sala)."""
        return (
            self._turma is outra.turma
            and self._dia == outra.dia
            and self._intervalo == outra.intervalo
            and self._sala == outra.sala
        )

    def __str__(self) -> str:
        return f"{self._dia} {self._intervalo}, {self._sala}"

    def __repr__(self) -> str:
        return (f"Aula({self.disciplina.codigo} {self._turma.codigo}, "
                f"{self._dia.sigla} {self._intervalo}, {self._sala.identificador})")
