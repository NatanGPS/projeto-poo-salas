"""Testes do menu do terminal com entradas digitadas simuladas."""

import unittest

from apoio import novo_catalogo, retrato
from guia_salas.servicos.consulta import ConsultaDeSalas
from guia_salas.terminal import MenuTerminal


class TestMenu(unittest.TestCase):

    def executar(self, entradas):
        """Executa o menu com as entradas dadas e devolve tudo o que foi escrito."""
        self.catalogo = novo_catalogo()
        self.antes = retrato(self.catalogo)
        fila = iter(entradas)
        saida = []

        def ler(_):
            """Devolve a próxima entrada; sem entradas, age como input() no fim do arquivo."""
            try:
                return next(fila)
            except StopIteration:
                raise EOFError from None

        MenuTerminal(ConsultaDeSalas(self.catalogo), "Base de teste.",
                     ler=ler, escrever=saida.append).executar()
        return "\n".join(saida)

    def test_busca_pelo_menu(self):
        saida = self.executar(["1", "banco de dados", "0"])
        self.assertIn("DCC011 - INTRODUCAO A BANCO DE DADOS", saida)
        self.assertIn("sala 2014 - DCC (ICEx, 2º andar)", saida)

    def test_andar_nao_numerico_e_recusado_e_menu_continua(self):
        saida = self.executar(["2", "ter", "14:00", "dois", "1", "dcc024", "0"])
        self.assertIn('Andar inválido: "dois". Use um número, como 2.', saida)
        self.assertIn("DCC024 - LINGUAGENS DE PROGRAMACAO", saida)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_hora_invalida_e_opcao_invalida(self):
        saida = self.executar(["2", "seg", "25:00", "x", "0"])
        self.assertIn("Horário inválido: '25:00'", saida)
        self.assertIn("Opção inválida. Digite 1, 2 ou 0.", saida)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_fim_da_entrada_encerra_sem_erro(self):
        saida = self.executar([])
        self.assertTrue(saida.endswith("Encerrado."))


if __name__ == "__main__":
    unittest.main()
