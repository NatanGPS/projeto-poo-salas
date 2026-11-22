"""Interface comum das fontes de dados."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass


class FonteIndisponivel(Exception):
    """A fonte não pôde ser consultada."""


@dataclass(frozen=True)
class RegistroDeAula:
    """Registro de aula como veio da fonte, ainda sem validação."""

    codigo: str
    nome: str
    turma: str
    dias: str
    inicio: str
    fim: str
    sala: str
    predio: str
    andar: int | None
    origem: str


class FonteDeDados(ABC):
    """Fonte de registros de aulas."""

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome curto da fonte, usado para indicar a origem dos dados."""

    @abstractmethod
    def coletar(self) -> list[RegistroDeAula]:
        """Obtém os registros de aulas da fonte."""


def andar_pelo_numero(sala: str) -> int | None:
    """Deduz o andar pelo primeiro dígito do número da sala: 1024 fica no 1º andar, 310 no 3º."""
    numero = re.search(r"\d{3,4}", sala)
    return int(numero.group()[0]) if numero else None
