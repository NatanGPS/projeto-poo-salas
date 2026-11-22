"""Camada de dados: fontes de registros de aulas e base SQLite."""

from guia_salas.dados.banco import BancoDeDados, FalhaNaBase
from guia_salas.dados.fonte_banco import FonteBancoLocal
from guia_salas.dados.fonte_base import FonteDeDados, FonteIndisponivel, RegistroDeAula
from guia_salas.dados.fonte_icex import AMOSTRA, URL_DADOS, FonteIcex, FonteIcexArquivo, FonteIcexOnline
from guia_salas.dados.repositorios import (
    GradeSalva,
    RegistroDeAtualizacao,
    RepositorioDeAulas,
    RepositorioDeGrades,
)

__all__ = [
    "AMOSTRA",
    "BancoDeDados",
    "FalhaNaBase",
    "FonteBancoLocal",
    "FonteDeDados",
    "FonteIcex",
    "FonteIcexArquivo",
    "FonteIcexOnline",
    "FonteIndisponivel",
    "GradeSalva",
    "RegistroDeAtualizacao",
    "RegistroDeAula",
    "RepositorioDeAulas",
    "RepositorioDeGrades",
    "URL_DADOS",
]
