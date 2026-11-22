"""Conceitos do domínio: disciplinas, turmas, aulas e salas."""

from guia_salas.dominio.aula import Aula
from guia_salas.dominio.dia_semana import DiaSemana
from guia_salas.dominio.disciplina import Disciplina
from guia_salas.dominio.erros import (
    ConflitoDeHorario,
    DadoInvalido,
    ErroDeDominio,
    PredioDesconhecido,
    TermoDeBuscaInvalido,
)
from guia_salas.dominio.intervalo import IntervaloDeHorario
from guia_salas.dominio.sala import Sala
from guia_salas.dominio.turma import Turma

__all__ = [
    "Aula",
    "ConflitoDeHorario",
    "DadoInvalido",
    "DiaSemana",
    "Disciplina",
    "ErroDeDominio",
    "IntervaloDeHorario",
    "PredioDesconhecido",
    "Sala",
    "TermoDeBuscaInvalido",
    "Turma",
]
