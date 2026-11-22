"""Testes das fontes de dados: a mesma operação coletar() em duas classes concretas."""

import json
import unittest

from apoio import REGISTROS_TESTE
from guia_salas.fontes import FonteDeDados, FonteIcexArquivo, FonteIcexOnline, FonteIndisponivel
from guia_salas.fontes.icex import separar_predio
from guia_salas.servicos.atualizador import AtualizadorDeBase


class RespostaFalsa:
    """Substitui a resposta HTTP do site do ICEx."""

    def __init__(self, dados):
        self._dados = dados

    def raise_for_status(self):
        pass

    def json(self):
        return self._dados


class SessaoFalsa:
    """Substitui a sessão do requests e registra os endereços pedidos, sem acessar a internet."""

    def __init__(self, dados):
        self._dados = dados
        self.enderecos = []

    def get(self, url, **_):
        self.enderecos.append(url)
        return RespostaFalsa(self._dados)


class TestFontes(unittest.TestCase):

    def setUp(self):
        self.dados = json.loads(REGISTROS_TESTE.read_text(encoding="utf-8"))
        self.sessao = SessaoFalsa(self.dados)
        self.fontes: list[FonteDeDados] = [
            FonteIcexArquivo(REGISTROS_TESTE),
            FonteIcexOnline("https://exemplo.invalido/recupera_salas.php", sessao=self.sessao),
        ]

    def test_duas_fontes_concretas_entregam_os_mesmos_registros(self):
        resultados = [fonte.coletar() for fonte in self.fontes]
        self.assertEqual(11, len(resultados[0]))
        self.assertEqual(resultados[0], resultados[1])
        self.assertEqual(["https://exemplo.invalido/recupera_salas.php"], self.sessao.enderecos)

    def test_atualizador_monta_o_mesmo_catalogo_com_qualquer_fonte(self):
        tamanhos = []
        for fonte in self.fontes:
            catalogo, relatorio = AtualizadorDeBase([fonte]).atualizar()
            self.assertEqual([], relatorio.recusados)
            tamanhos.append((len(catalogo.disciplinas), len(catalogo)))
        self.assertEqual([(7, 19), (7, 19)], tamanhos)

    def test_arquivo_inexistente_vira_falha_no_relatorio(self):
        catalogo, relatorio = AtualizadorDeBase([FonteIcexArquivo("nao_existe.json")]).atualizar()
        self.assertEqual(0, len(catalogo))
        self.assertIn("ICEx", relatorio.fontes_com_falha)

    def test_arquivo_inexistente_lanca_fonte_indisponivel(self):
        with self.assertRaises(FonteIndisponivel):
            FonteIcexArquivo("nao_existe.json").coletar()

    def test_separacao_de_predio_e_sala(self):
        self.assertEqual(("ICEx", "2014 - DCC"), separar_predio("2014 - DCC"))
        self.assertEqual(("CAD3", "310"), separar_predio("CAD3 - Sala 310"))
        self.assertEqual(("ICEx", "AUD. II"), separar_predio("AUD. II - ICEX"))
        self.assertEqual(("On-line", "ON-LINE"), separar_predio("ON-LINE"))


if __name__ == "__main__":
    unittest.main()
