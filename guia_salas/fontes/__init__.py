"""Fontes de dados de aulas."""

from guia_salas.fontes.base import FonteDeDados, FonteIndisponivel, RegistroDeAula
from guia_salas.fontes.icex import AMOSTRA, URL_DADOS, FonteIcex, FonteIcexArquivo, FonteIcexOnline

__all__ = [
    "AMOSTRA",
    "FonteDeDados",
    "FonteIcex",
    "FonteIcexArquivo",
    "FonteIcexOnline",
    "FonteIndisponivel",
    "RegistroDeAula",
    "URL_DADOS",
]
