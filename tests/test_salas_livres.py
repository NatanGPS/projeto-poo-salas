"""Testes da funcionalidade F02: consultar salas livres."""

import unittest
from datetime import time

from apoio import novo_catalogo, retrato
from guia_salas.dominio import DadoInvalido, DiaSemana, IntervaloDeHorario, PredioDesconhecido
from guia_salas.servicos.consulta import ConsultaDeSalas


class TestSalasLivres(unittest.TestCase):
    """Cada teste usa um catálogo novo, montado a partir de tests/dados/registros_teste.json."""

    def setUp(self):
        self.catalogo = novo_catalogo()
        self.consulta = ConsultaDeSalas(self.catalogo)
        self.antes = retrato(self.catalogo)

    def identificadores(self, dia, instante, andar=None, predio=None):
        return [s.identificador for s in self.consulta.salas_livres(dia, instante, andar, predio)]

    def test_sala_ocupada_nao_aparece(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(9, 30), 2, "icex")
        self.assertEqual(["2009 - DCC", "2013 - DCC"], livres)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_sala_fica_livre_no_horario_de_termino(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(11, 5), 2, "ICEx")
        self.assertIn("2014 - DCC", livres)

    def test_turma_conjunta_ocupa_a_sala(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(15, 0), None, "CAD3")
        self.assertNotIn("407", livres)
        sala_407 = next(s for s in self.catalogo.salas if s.chave == ("cad3", "407"))
        ocupantes = self.catalogo.turmas_na_sala(sala_407, DiaSemana.SEGUNDA,
                                                 IntervaloDeHorario.de_texto("14:55", "16:35"))
        self.assertEqual(["DCC006", "DCC017"], sorted(a.disciplina.codigo for a in ocupantes))

    def test_aula_online_nao_vira_sala_livre(self):
        todas = self.identificadores(DiaSemana.SEXTA, time(11, 30))
        self.assertNotIn("ON-LINE", todas)

    def test_predio_desconhecido_e_rejeitado_sem_alterar_catalogo(self):
        with self.assertRaises(PredioDesconhecido):
            self.consulta.salas_livres(DiaSemana.TERCA, time(14, 0), 1, "CAD9")
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_andar_negativo_e_rejeitado(self):
        with self.assertRaises(DadoInvalido):
            self.consulta.salas_livres(DiaSemana.TERCA, time(14, 0), -1)
        self.assertEqual(self.antes, retrato(self.catalogo))


if __name__ == "__main__":
    unittest.main()
