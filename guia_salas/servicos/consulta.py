"""Consultas feitas pelo aluno."""

from dataclasses import dataclass, field
from datetime import time

from guia_salas.dominio import (
    DadoInvalido,
    DiaSemana,
    Disciplina,
    PredioDesconhecido,
    Sala,
    TermoDeBuscaInvalido,
)
from guia_salas.servicos.catalogo import CatalogoDeAulas

TAMANHO_MINIMO_DO_TERMO = 3


@dataclass(frozen=True)
class ResultadoDaBusca:
    """Disciplinas encontradas para um termo de busca."""

    termo: str
    disciplinas: list[Disciplina] = field(default_factory=list)

    @property
    def encontrou(self) -> bool:
        """Indica se ao menos uma disciplina corresponde ao termo."""
        return bool(self.disciplinas)


class ConsultaDeSalas:
    """Consultas F01 (sala da disciplina) e F02 (salas livres) sobre o catálogo."""

    def __init__(self, catalogo: CatalogoDeAulas):
        """Recebe o catálogo que será consultado."""
        self._catalogo = catalogo

    @property
    def catalogo(self) -> CatalogoDeAulas:
        """Catálogo usado nas consultas (somente leitura)."""
        return self._catalogo

    def trocar_catalogo(self, novo: CatalogoDeAulas) -> None:
        """Passa a responder com um catálogo recém-atualizado; recusa um catálogo vazio e mantém o atual."""
        if len(novo) == 0:
            raise DadoInvalido("O catálogo novo está vazio; a base atual foi mantida.")
        self._catalogo = novo

    def buscar_por_disciplina(self, termo: str) -> ResultadoDaBusca:
        """Busca disciplinas por código ou nome; rejeita termos com menos de 3 caracteres."""
        termo = " ".join(termo.split())
        if len(termo) < TAMANHO_MINIMO_DO_TERMO:
            raise TermoDeBuscaInvalido(
                f"Informe ao menos {TAMANHO_MINIMO_DO_TERMO} caracteres do nome ou o código da disciplina."
            )
        return ResultadoDaBusca(termo, self._catalogo.buscar_disciplinas(termo))

    def salas_livres(self, dia: DiaSemana, instante: time, andar: int | None = None,
                     predio: str | None = None) -> list[Sala]:
        """Salas presenciais sem aula no dia e instante informados."""
        if andar is not None and andar < 0:
            raise DadoInvalido("O andar não pode ser negativo.")
        if predio:
            conhecidos = {p.casefold(): p for p in self._catalogo.predios}
            if predio.strip().casefold() not in conhecidos:
                raise PredioDesconhecido(
                    f"Prédio \"{predio.strip()}\" não encontrado. Prédios na base: {', '.join(self._catalogo.predios)}."
                )
            predio = conhecidos[predio.strip().casefold()]
        return self._catalogo.salas_livres(dia, instante, andar, predio or None)
