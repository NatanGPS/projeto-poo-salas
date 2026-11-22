"""Dias da semana em que pode haver aula."""

import re
from enum import Enum

from guia_salas.dominio.erros import DadoInvalido
from guia_salas.texto import normalizar


class DiaSemana(Enum):
    """Dia letivo da semana."""

    SEGUNDA = ("SEG", "Segunda", 2)
    TERCA = ("TER", "Terça", 3)
    QUARTA = ("QUA", "Quarta", 4)
    QUINTA = ("QUI", "Quinta", 5)
    SEXTA = ("SEX", "Sexta", 6)
    SABADO = ("SAB", "Sábado", 7)

    def __init__(self, sigla: str, nome: str, numero: int):
        self.sigla = sigla
        self.nome = nome
        self.numero = numero

    def __str__(self) -> str:
        return self.nome

    @classmethod
    def de_texto(cls, texto: str) -> "DiaSemana":
        """Converte textos como 'Seg', 'terça', 'SEXTA' ou '2ª' em um dia."""
        limpo = normalizar(texto)
        if limpo[:1].isdigit():
            numero = int(limpo[:1])
            for dia in cls:
                if dia.numero == numero:
                    return dia
        for dia in cls:
            if limpo[:3] == dia.sigla.lower():
                return dia
        raise DadoInvalido(f"Dia da semana desconhecido: {texto!r}")

    @classmethod
    def varios_de_texto(cls, texto: str) -> list["DiaSemana"]:
        """Converte listas como 'SEG QUA', 'Seg/Qua' ou '2ª, 4ª' em dias."""
        partes = re.split(r"[\s/,;-]+", normalizar(texto))
        return [cls.de_texto(p) for p in partes if p]
