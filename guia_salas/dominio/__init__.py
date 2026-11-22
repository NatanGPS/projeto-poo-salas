"""Conceitos do domínio: disciplinas, turmas, aulas, salas e a grade do aluno."""

from guia_salas.dominio.aula import Aula
from guia_salas.dominio.dia_semana import DiaSemana
from guia_salas.dominio.disciplina import Disciplina
from guia_salas.dominio.erros import (
    AtualizacaoRecusada,
    ConflitoDeHorario,
    DadoInvalido,
    Duplicidade,
    ErroDeDominio,
    GravacaoFalhou,
    LimiteExcedido,
    NaoEncontrado,
    PlanilhaInvalida,
    PredioDesconhecido,
    TermoDeBuscaInvalido,
)
from guia_salas.dominio.grade_do_aluno import LIMITE_DE_DISCIPLINAS, GradeDoAluno
from guia_salas.dominio.intervalo import IntervaloDeHorario, ler_hora
from guia_salas.dominio.sala import PREDIO_ONLINE, Sala, SalaOnline
from guia_salas.dominio.turma import Turma

__all__ = [
    "AtualizacaoRecusada",
    "Aula",
    "ConflitoDeHorario",
    "DadoInvalido",
    "DiaSemana",
    "Disciplina",
    "Duplicidade",
    "ErroDeDominio",
    "GradeDoAluno",
    "GravacaoFalhou",
    "IntervaloDeHorario",
    "LIMITE_DE_DISCIPLINAS",
    "LimiteExcedido",
    "NaoEncontrado",
    "PREDIO_ONLINE",
    "PlanilhaInvalida",
    "PredioDesconhecido",
    "Sala",
    "SalaOnline",
    "TermoDeBuscaInvalido",
    "Turma",
    "ler_hora",
]
