"""Turma de uma disciplina."""

from typing import TYPE_CHECKING

from guia_salas.dominio.aula import Aula
from guia_salas.dominio.dia_semana import DiaSemana
from guia_salas.dominio.erros import ConflitoDeHorario, DadoInvalido
from guia_salas.dominio.intervalo import IntervaloDeHorario
from guia_salas.dominio.sala import Sala

if TYPE_CHECKING:
    from guia_salas.dominio.disciplina import Disciplina


class Turma:
    """Oferta de uma disciplina no semestre, com suas aulas semanais."""

    def __init__(self, codigo: str, disciplina: "Disciplina"):
        """Valida o código, guardado sem espaços e em maiúsculas; deve ser criada por Disciplina.obter_turma."""
        codigo = "".join(codigo.split()).upper()
        if not codigo:
            raise DadoInvalido("A turma precisa de um código.")
        self._codigo = codigo
        self._disciplina = disciplina
        self._aulas: list[Aula] = []

    @property
    def codigo(self) -> str:
        """Código da turma, sem espaços, como TB ou TM2/TN3."""
        return self._codigo

    @property
    def disciplina(self) -> "Disciplina":
        """Disciplina que oferece a turma."""
        return self._disciplina

    @property
    def aulas(self) -> list[Aula]:
        """Aulas da turma ordenadas por dia e horário de início."""
        return sorted(self._aulas, key=lambda a: (a.dia.numero, a.intervalo.inicio))

    def agendar_aula(self, dia: DiaSemana, intervalo: IntervaloDeHorario,
                     sala: Sala, origem: str) -> Aula:
        """Cria e registra uma aula; devolve a existente se o encontro já estiver registrado."""
        nova = Aula(self, dia, intervalo, sala, origem)
        for existente in self._aulas:
            if existente.mesmo_encontro(nova):
                return existente
            if existente.dia == dia and existente.intervalo.sobrepoe(intervalo):
                raise ConflitoDeHorario(
                    f"A turma {self._disciplina.codigo} {self._codigo} já tem aula "
                    f"{existente.dia} {existente.intervalo}."
                )
        self._aulas.append(nova)
        return nova

    def __str__(self) -> str:
        return f"Turma {self._codigo}"
