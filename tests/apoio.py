"""Dados e funções compartilhados pelos testes."""

import shutil
import tempfile
import unittest
from pathlib import Path

from guia_salas.dados import BancoDeDados, FonteIcexArquivo
from guia_salas.servicos.atualizador import AtualizadorDeBase
from guia_salas.servicos.catalogo import CatalogoDeAulas
from guia_salas.sistema import Sistema, abrir_sistema

PASTA_DADOS = Path(__file__).resolve().parent / "dados"
REGISTROS_TESTE = PASTA_DADOS / "registros_teste.json"
REGISTROS_GRADE_CHEIA = PASTA_DADOS / "registros_grade_cheia.json"
PLANILHA_EXEMPLO = Path(__file__).resolve().parent.parent / "exemplos" / "grade_exemplo.xlsx"
TABELAS = ("disciplina", "turma", "sala", "aula", "atualizacao", "grade", "grade_turma")


def novo_catalogo(registros: Path = REGISTROS_TESTE) -> CatalogoDeAulas:
    """Catálogo em memória com os 11 registros reais de tests/dados (7 disciplinas, 19 aulas)."""
    catalogo, _ = AtualizadorDeBase([FonteIcexArquivo(registros)]).atualizar()
    return catalogo


def retrato(catalogo: CatalogoDeAulas) -> list[tuple]:
    """Lista ordenada de todas as aulas, usada para conferir que o catálogo não mudou."""
    return sorted(
        (a.disciplina.codigo, a.disciplina.nome, a.turma.codigo, a.dia.sigla, str(a.intervalo),
         a.sala.predio, a.sala.identificador, a.sala.andar)
        for a in catalogo.aulas()
    )


def retrato_banco(banco: BancoDeDados) -> dict[str, list[tuple]]:
    """Todas as linhas de todas as tabelas da base, para conferir que nada mudou."""
    with banco.transacao() as conexao:
        return {t: sorted(conexao.execute(f"SELECT * FROM {t}").fetchall(), key=repr) for t in TABELAS}


class TesteComBase(unittest.TestCase):
    """Cada teste recebe uma base SQLite nova numa pasta temporária, separada da base de demonstração."""

    REGISTROS = REGISTROS_TESTE

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="guia_salas_teste_"))
        self.addCleanup(shutil.rmtree, self.pasta, ignore_errors=True)
        self.sistema: Sistema = abrir_sistema(self.pasta / "teste.db")
        self.sistema.atualizacao.atualizar(FonteIcexArquivo(self.REGISTROS))

    def reabrir(self) -> Sistema:
        """Abre de novo a mesma base, como se o programa tivesse sido reiniciado."""
        return abrir_sistema(self.pasta / "teste.db")
