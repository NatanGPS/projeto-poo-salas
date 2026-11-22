"""F02: consultar salas livres num dia, hora, andar e prédio."""

import unittest
from datetime import time

from apoio import TesteComBase, novo_catalogo, retrato, retrato_banco
from guia_salas.apresentacao.comandos import ComandosDoBot
from guia_salas.dominio import DadoInvalido, DiaSemana, IntervaloDeHorario, PredioDesconhecido, ler_hora
from guia_salas.servicos.consulta import ConsultaDeSalas


class TestF02SalasLivres(unittest.TestCase):
    """Estado inicial: catálogo novo com os 11 registros de tests/dados/registros_teste.json."""

    def setUp(self):
        self.catalogo = novo_catalogo()
        self.consulta = ConsultaDeSalas(self.catalogo)
        self.antes = retrato(self.catalogo)

    def identificadores(self, dia, instante, andar=None, predio=None):
        return [s.identificador for s in self.consulta.salas_livres(dia, instante, andar, predio)]

    def test_c01_sala_ocupada_nao_aparece(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(9, 30), 2, "icex")
        self.assertEqual(["2009 - DCC", "2013 - DCC"], livres)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c02_sala_fica_livre_no_horario_de_termino(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(11, 5), 2, "ICEx")
        self.assertIn("2014 - DCC", livres)

    def test_c03_sala_ocupada_no_horario_de_inicio(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(9, 25), 2, "ICEx")
        self.assertNotIn("2014 - DCC", livres)

    def test_c04_turma_conjunta_ocupa_a_sala(self):
        livres = self.identificadores(DiaSemana.SEGUNDA, time(15, 0), None, "CAD3")
        self.assertNotIn("407", livres)
        sala_407 = next(s for s in self.catalogo.salas if s.chave == ("cad3", "407"))
        ocupantes = self.catalogo.turmas_na_sala(sala_407, DiaSemana.SEGUNDA,
                                                 IntervaloDeHorario.de_texto("14:55", "16:35"))
        self.assertEqual(["DCC006", "DCC017"], sorted(a.disciplina.codigo for a in ocupantes))

    def test_c05_aula_online_nunca_vira_sala_livre(self):
        todas = self.identificadores(DiaSemana.SEXTA, time(18, 0))
        self.assertNotIn("ON-LINE", todas)

    def test_c06_predio_desconhecido_e_rejeitado_sem_alterar_catalogo(self):
        with self.assertRaises(PredioDesconhecido):
            self.consulta.salas_livres(DiaSemana.TERCA, time(14, 0), 1, "CAD9")
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c07_andar_negativo_e_rejeitado(self):
        with self.assertRaises(DadoInvalido):
            self.consulta.salas_livres(DiaSemana.TERCA, time(14, 0), -1)
        self.assertEqual(self.antes, retrato(self.catalogo))

    def test_c08_hora_e_dia_invalidos_sao_rejeitados_na_conversao(self):
        for texto in ("25:00", "14", "dez horas", "-1:00"):
            with self.assertRaises(DadoInvalido):
                ler_hora(texto)
        with self.assertRaises(DadoInvalido):
            DiaSemana.de_texto("domingo")

    def test_c09_andar_sem_salas_devolve_lista_vazia_valida(self):
        self.assertEqual([], self.identificadores(DiaSemana.SEGUNDA, time(9, 30), 9))


class TestF02ComandoDoBot(TesteComBase):
    """Estado inicial: base de teste em pasta temporária com os registros de tests/dados."""

    def test_c10_livres_sem_andar_considera_todos_e_aceita_predio(self):
        antes = retrato_banco(self.sistema.banco)
        resposta = ComandosDoBot(self.sistema).livres("seg 09:30 icex")
        self.assertIn("Salas livres (Segunda, 09:30):", resposta)
        self.assertIn("1012 (ICEx)", resposta)
        self.assertNotIn("2014 - DCC", resposta)
        self.assertEqual(antes, retrato_banco(self.sistema.banco))

    def test_c11_livres_com_hora_invalida_mostra_motivo_e_uso(self):
        resposta = ComandosDoBot(self.sistema).livres("ter 25:00 1")
        self.assertIn("Horário inválido: '25:00'", resposta)
        self.assertIn("Uso: /livres", resposta)

    def test_c12_livres_sem_hora_mostra_uso(self):
        self.assertTrue(ComandosDoBot(self.sistema).livres("ter").startswith("Uso: /livres"))


if __name__ == "__main__":
    unittest.main()
