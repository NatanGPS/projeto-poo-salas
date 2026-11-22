"""Dados conhecidos compartilhados pelos testes."""

from pathlib import Path

from guia_salas.fontes import FonteIcexArquivo
from guia_salas.servicos.atualizador import AtualizadorDeBase
from guia_salas.servicos.catalogo import CatalogoDeAulas

REGISTROS_TESTE = Path(__file__).resolve().parent / "dados" / "registros_teste.json"


def novo_catalogo() -> CatalogoDeAulas:
    """Catálogo novo com os 11 registros reais de tests/dados (7 disciplinas, 19 aulas)."""
    catalogo, _ = AtualizadorDeBase([FonteIcexArquivo(REGISTROS_TESTE)]).atualizar()
    return catalogo


def retrato(catalogo: CatalogoDeAulas) -> list[tuple]:
    """Lista ordenada de todas as aulas, usada para conferir que o catálogo não mudou."""
    return sorted(
        (a.disciplina.codigo, a.disciplina.nome, a.turma.codigo, a.dia.sigla, str(a.intervalo),
         a.sala.predio, a.sala.identificador, a.sala.andar)
        for a in catalogo.aulas()
    )
