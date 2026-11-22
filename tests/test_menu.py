"""Menu do terminal com entradas digitadas simuladas."""

import shutil
import unittest

from apoio import PLANILHA_EXEMPLO, TesteComBase, retrato_banco
from guia_salas.apresentacao.terminal import MenuTerminal


class TestMenu(TesteComBase):
    """Estado inicial: base de teste com os registros de tests/dados."""

    def executar(self, entradas):
        """Executa o menu com as entradas dadas e devolve tudo o que foi escrito."""
        fila = iter(entradas)
        saida = []

        def ler(_):
            """Devolve a próxima entrada; sem entradas, age como input() no fim do arquivo."""
            try:
                return next(fila)
            except StopIteration:
                raise EOFError from None

        MenuTerminal(self.sistema, ler=ler, escrever=saida.append).executar()
        return "\n".join(saida)

    def test_abertura_mostra_a_base_e_a_ultima_atualizacao(self):
        saida = self.executar(["0"])
        self.assertIn("Base: 7 disciplinas, 19 aulas. Última atualização:", saida)
        self.assertIn("arquivo registros_teste.json", saida)

    def test_busca_pelo_menu(self):
        saida = self.executar(["1", "banco de dados", "0"])
        self.assertIn("DCC011 - INTRODUCAO A BANCO DE DADOS", saida)
        self.assertIn("sala 2014 - DCC (ICEx, 2º andar)", saida)

    def test_andar_nao_numerico_e_recusado_e_menu_continua(self):
        antes = retrato_banco(self.sistema.banco)
        saida = self.executar(["2", "ter", "14:00", "dois", "1", "dcc024", "0"])
        self.assertIn('Entrada recusada: Andar inválido: "dois". Use um número, como 2.', saida)
        self.assertIn("DCC024 - LINGUAGENS DE PROGRAMACAO", saida)
        self.assertEqual(antes, retrato_banco(self.sistema.banco))

    def test_hora_invalida_e_opcao_invalida(self):
        saida = self.executar(["2", "seg", "25:00", "x", "0"])
        self.assertIn("Horário inválido: '25:00'", saida)
        self.assertIn("Opção inválida. Digite um número de 0 a 5.", saida)

    def test_planilha_pelo_menu(self):
        entrada = self.pasta / "grade.xlsx"
        shutil.copy(PLANILHA_EXEMPLO, entrada)
        saida = self.executar(["3", f'"{entrada}"', "0"])
        self.assertIn("3 disciplina(s) localizada(s), 1 não localizada(s).", saida)
        self.assertTrue((self.pasta / "grade_com_salas.xlsx").exists())

    def test_minha_grade_pelo_menu(self):
        saida = self.executar(["4", "ana", "2", "DCC011 TB", "2", "DCC001 TB", "4", "Ana", "1", "0", "0"])
        self.assertIn("Adicionada(s) à grade: DCC011 TB.", saida)
        self.assertIn("Entrada recusada: DCC011 TB (Segunda 09:25-11:05) conflita com DCC001 TB", saida)
        self.assertIn("Nome alterado para Ana.", saida)
        self.assertIn("Grade: Ana (1 disciplina(s))", saida)

    def test_atualizacao_recusada_pelo_menu_mantem_a_base(self):
        antes = retrato_banco(self.sistema.banco)
        saida = self.executar(["5", "2", str(self.pasta / "nao_existe.json"), "5", "9", "0"])
        self.assertIn("A base anterior foi mantida.", saida)
        self.assertIn("Origem inválida. Digite 1 ou 2.", saida)
        self.assertEqual(antes, retrato_banco(self.sistema.banco))

    def test_fim_da_entrada_encerra_sem_erro(self):
        saida = self.executar(["4", "ana"])
        self.assertTrue(saida.endswith("Encerrado."))


if __name__ == "__main__":
    unittest.main()
