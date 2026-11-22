"""Testes da funcionalidade F01: buscar a sala de uma disciplina."""

import unittest

from apoio import novo_catalogo, retrato
from guia_salas.dominio import TermoDeBuscaInvalido
from guia_salas.servicos.consulta import ConsultaDeSalas


class TestBuscaDisciplina(unittest.TestCase):
    """Cada teste usa um catálogo novo, montado a partir de tests/dados/registros_teste.json."""

    def setUp(self):
        self.catalogo = novo_catalogo()
        self.consulta = ConsultaDeSalas(self.catalogo)
        self.antes = retrato(self.catalogo)

    def test_busca_por_nome_devolve_turmas_e_salas(self):
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

    def test_busca_por_codigo_ignora_maiusculas(self):
        resultado = self.consulta.buscar_por_disciplina("dcc024")
        self.assertEqual(["DCC024"], [d.codigo for d in resultado.disciplinas])
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_termo_curto_e_rejeitado_sem_alterar_catalogo(self):
        with self.assertRaises(TermoDeBuscaInvalido):
            self.consulta.buscar_por_disciplina("  C ")
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_disciplina_ausente_devolve_resultado_vazio_valido(self):
        resultado = self.consulta.buscar_por_disciplina("Programação Orientada a Objetos")
        self.assertFalse(resultado.encontrou)
        self.assertEqual([], resultado.disciplinas)
        self.assertEqual(self.antes, retrato(self.catalogo))


if __name__ == "__main__":
    unittest.main()
