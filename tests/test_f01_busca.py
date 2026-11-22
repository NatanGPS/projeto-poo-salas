"""F01: buscar a sala de uma disciplina pelo nome ou código."""

import unittest

from apoio import TesteComBase, novo_catalogo, retrato, retrato_banco
from guia_salas.apresentacao.comandos import ComandosDoBot
from guia_salas.apresentacao.formatacao import dividir_mensagem
from guia_salas.dominio import TermoDeBuscaInvalido
from guia_salas.servicos.consulta import ConsultaDeSalas


class TestF01Busca(unittest.TestCase):
    """Estado inicial: catálogo novo com os 11 registros de tests/dados/registros_teste.json."""

    def setUp(self):
        self.catalogo = novo_catalogo()
        self.consulta = ConsultaDeSalas(self.catalogo)
        self.antes = retrato(self.catalogo)

    def test_c01_busca_por_nome_devolve_turmas_e_salas(self):
        resultado = self.consulta.buscar_por_disciplina("banco de dados")
        self.assertEqual(["DCC011"], [d.codigo for d in resultado.disciplinas])
        aulas = [(a.turma.codigo, a.dia.sigla, str(a.intervalo), a.sala.predio, a.sala.identificador)
                 for a in resultado.disciplinas[0].aulas()]
        self.assertEqual([
            ("TB", "SEG", "09:25-11:05", "ICEx", "2014 - DCC"),
            ("TB", "QUA", "09:25-11:05", "ICEx", "2014 - DCC"),
            ("TE", "TER", "19:00-20:40", "CAD3", "213"),
            ("TE", "QUI", "19:00-20:40", "CAD3", "213"),
        ], aulas)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c02_busca_por_codigo_ignora_maiusculas_e_espacos(self):
        resultado = self.consulta.buscar_por_disciplina("  dcc024 ")
        self.assertEqual(["DCC024"], [d.codigo for d in resultado.disciplinas])
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c03_algarismo_equivale_a_romano_e_acentos_sao_ignorados(self):
        resultado = self.consulta.buscar_por_disciplina("Cálculo 1")
        self.assertEqual(["MAT001"], [d.codigo for d in resultado.disciplinas])

    def test_c04_termo_com_tres_caracteres_e_aceito(self):
        resultado = self.consulta.buscar_por_disciplina("ban")
        self.assertEqual(["DCC011"], [d.codigo for d in resultado.disciplinas])

    def test_c05_termo_curto_e_rejeitado_sem_alterar_catalogo(self):
        with self.assertRaises(TermoDeBuscaInvalido):
            self.consulta.buscar_por_disciplina("  C ")
        with self.assertRaises(TermoDeBuscaInvalido):
            self.consulta.buscar_por_disciplina("ba")
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c06_disciplina_ausente_devolve_resultado_vazio_valido(self):
        resultado = self.consulta.buscar_por_disciplina("Programação Orientada a Objetos")
        self.assertFalse(resultado.encontrou)
        self.assertEqual([], resultado.disciplinas)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c07_termo_comum_a_varias_disciplinas_devolve_todas(self):
        resultado = self.consulta.buscar_por_disciplina("computadores")
        self.assertEqual(["DCC001", "DCC006", "DCC017"], [d.codigo for d in resultado.disciplinas])


class TestF01ComandoDoBot(TesteComBase):
    """Estado inicial: base de teste em pasta temporária com os registros de tests/dados."""

    def test_c08_comando_sala_responde_e_nao_altera_a_base(self):
        antes = retrato_banco(self.sistema.banco)
        resposta = ComandosDoBot(self.sistema).sala("DCC011")
        self.assertIn("DCC011 - INTRODUCAO A BANCO DE DADOS", resposta)
        self.assertIn("TE: Ter/Qui 19:00-20:40, sala 213 (CAD3, 2º andar)", resposta)
        self.assertEqual(antes, retrato_banco(self.sistema.banco))

    def test_c09_comando_sala_com_termo_curto_mostra_exemplo(self):
        resposta = ComandosDoBot(self.sistema).sala("C")
        self.assertIn("Informe ao menos 3 caracteres", resposta)
        self.assertIn("Exemplo: /sala banco de dados", resposta)

    def test_c10_resposta_longa_e_dividida_entre_linhas(self):
        texto = "\n".join(f"linha {i:04d}" for i in range(1000))
        partes = dividir_mensagem(texto, limite=4000)
        self.assertTrue(all(len(p) <= 4000 for p in partes))
        self.assertEqual(texto, "\n".join(partes))


if __name__ == "__main__":
    unittest.main()
