"""F03: preencher a planilha de disciplinas com turma, horários e sala."""

import hashlib
import shutil
import unittest

from openpyxl import Workbook, load_workbook

from apoio import PLANILHA_EXEMPLO, TesteComBase, retrato_banco
from guia_salas.apresentacao.comandos import ComandosDoBot
from guia_salas.dominio import PlanilhaInvalida
from guia_salas.servicos.planilha import NAO_LOCALIZADA


def resumo(caminho) -> str:
    """Hash do conteúdo do arquivo, para conferir que ele não mudou."""
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


class TestF03Planilha(TesteComBase):
    """Estado inicial: base de teste com os registros de tests/dados e uma cópia de exemplos/grade_exemplo.xlsx."""

    def setUp(self):
        super().setUp()
        self.entrada = self.pasta / "grade.xlsx"
        shutil.copy(PLANILHA_EXEMPLO, self.entrada)
        self.hash_entrada = resumo(self.entrada)
        self.base_antes = retrato_banco(self.sistema.banco)
        self.preenchedor = self.sistema.planilha

    def nova_planilha(self, linhas, nome="nova.xlsx"):
        """Cria uma planilha com as linhas dadas (a primeira é o cabeçalho)."""
        livro = Workbook()
        for linha in linhas:
            livro.active.append(linha)
        caminho = self.pasta / nome
        livro.save(caminho)
        return caminho

    def test_c01_planilha_de_exemplo_e_preenchida(self):
        resultado = self.preenchedor.preencher(self.entrada)
        self.assertEqual((3, 1), (resultado.localizadas, resultado.nao_localizadas))
        self.assertEqual(self.pasta / "grade_com_salas.xlsx", resultado.saida)
        linhas = list(load_workbook(resultado.saida).active.iter_rows(values_only=True))
        self.assertEqual(("Disciplina", "Turma", "Turma encontrada", "Dias e horários", "Sala"), linhas[0])
        self.assertEqual(("DCC011", "TB", "TB", "SEG 09:25-11:05; QUA 09:25-11:05", "2014 - DCC (ICEx)"), linhas[1])
        self.assertEqual("TE", linhas[2][2])
        self.assertEqual(("MAT038", "TM4", "TM4", "TER 13:00-14:40; QUI 13:00-14:40", "1012 (ICEx)"), linhas[3])
        self.assertEqual(NAO_LOCALIZADA, linhas[4][2])
        self.assertEqual(self.hash_entrada, resumo(self.entrada))
        self.assertEqual(self.base_antes, retrato_banco(self.sistema.banco))

    def test_c02_turma_pedida_inexistente_vira_nao_localizada(self):
        caminho = self.nova_planilha([("Disciplina", "Turma"), ("DCC011", "TZ"), ("DCC024", "")])
        resultado = self.preenchedor.preencher(caminho)
        self.assertEqual((1, 1), (resultado.localizadas, resultado.nao_localizadas))

    def test_c03_arquivo_inexistente_e_recusado(self):
        with self.assertRaises(PlanilhaInvalida):
            self.preenchedor.preencher(self.pasta / "nao_existe.xlsx")
        self.assertFalse((self.pasta / "nao_existe_com_salas.xlsx").exists())

    def test_c04_extensao_diferente_de_xlsx_e_recusada(self):
        caminho = self.pasta / "grade.csv"
        caminho.write_text("Disciplina\nDCC011\n", encoding="utf-8")
        with self.assertRaises(PlanilhaInvalida):
            self.preenchedor.preencher(caminho)

    def test_c05_arquivo_corrompido_e_recusado(self):
        caminho = self.pasta / "falsa.xlsx"
        caminho.write_text("isto não é uma planilha", encoding="utf-8")
        with self.assertRaises(PlanilhaInvalida):
            self.preenchedor.preencher(caminho)
        self.assertFalse((self.pasta / "falsa_com_salas.xlsx").exists())

    def test_c06_planilha_sem_disciplinas_e_recusada(self):
        caminho = self.nova_planilha([("Disciplina", "Turma")], "vazia.xlsx")
        with self.assertRaises(PlanilhaInvalida):
            self.preenchedor.preencher(caminho)
        self.assertFalse((self.pasta / "vazia_com_salas.xlsx").exists())

    def test_c07_saida_igual_a_entrada_e_recusada_e_original_preservado(self):
        with self.assertRaises(PlanilhaInvalida):
            self.preenchedor.preencher(self.entrada, self.entrada)
        self.assertEqual(self.hash_entrada, resumo(self.entrada))

    def test_c08_comando_do_bot_devolve_legenda(self):
        saida = self.pasta / "resposta.xlsx"
        legenda = ComandosDoBot(self.sistema).planilha(self.entrada, saida)
        self.assertEqual("3 disciplina(s) localizada(s), 1 não localizada(s).", legenda)
        self.assertTrue(saida.exists())


if __name__ == "__main__":
    unittest.main()
