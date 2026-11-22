"""Regras das classes do domínio: setters, especialização de Sala, intervalos e turmas."""

import unittest
from datetime import time

from guia_salas.dominio import (
    ConflitoDeHorario,
    DadoInvalido,
    DiaSemana,
    Disciplina,
    GradeDoAluno,
    IntervaloDeHorario,
    Sala,
    SalaOnline,
)


class TestSala(unittest.TestCase):

    def test_setter_do_andar_aceita_inteiro_nao_negativo_ou_none(self):
        sala = Sala("1012", "ICEx", 1)
        sala.andar = 0
        self.assertEqual(0, sala.andar)
        sala.andar = None
        self.assertIsNone(sala.andar)

    def test_setter_do_andar_recusa_negativo_e_texto_sem_alterar(self):
        sala = Sala("1012", "ICEx", 1)
        for valor in (-1, "2", 1.5, True):
            with self.assertRaises(DadoInvalido):
                sala.andar = valor
        self.assertEqual(1, sala.andar)

    def test_criar_devolve_a_especializacao_certa(self):
        self.assertIs(type(Sala.criar("1012", "ICEx", 1)), Sala)
        online = Sala.criar("ON-LINE", "on-line", None)
        self.assertIsInstance(online, SalaOnline)
        self.assertFalse(online.presencial)
        self.assertEqual("on-line", online.descricao())

    def test_sala_online_nunca_esta_livre_e_nao_tem_andar(self):
        online = SalaOnline()
        self.assertFalse(online.esta_livre(DiaSemana.SABADO, time(3, 0), []))
        with self.assertRaises(DadoInvalido):
            online.andar = 1

    def test_salas_com_mesma_chave_sao_iguais(self):
        self.assertEqual(Sala("Auditorio B-302", "CAD3", 3), Sala("AUDITORIO B-302", "cad3", None))


class TestIntervaloETurma(unittest.TestCase):

    def test_intervalos_encostados_nao_se_sobrepoem(self):
        primeiro = IntervaloDeHorario.de_texto("09:25", "11:05")
        self.assertFalse(primeiro.sobrepoe(IntervaloDeHorario.de_texto("11:05", "12:45")))
        self.assertTrue(primeiro.sobrepoe(IntervaloDeHorario.de_texto("11:04", "12:45")))

    def test_inicio_depois_do_fim_e_recusado(self):
        with self.assertRaises(DadoInvalido):
            IntervaloDeHorario.de_texto("11:05", "09:25")

    def test_turma_nao_aceita_aulas_sobrepostas(self):
        turma = Disciplina("DCC011", "Banco de Dados").obter_turma("TB")
        sala = Sala("2014 - DCC", "ICEx", 2)
        turma.agendar_aula(DiaSemana.SEGUNDA, IntervaloDeHorario.de_texto("09:25", "11:05"), sala, "teste")
        with self.assertRaises(ConflitoDeHorario):
            turma.agendar_aula(DiaSemana.SEGUNDA, IntervaloDeHorario.de_texto("10:00", "11:40"),
                               Sala("1012", "ICEx", 1), "teste")
        self.assertEqual(1, len(turma.aulas))


class TestGradeDoAluno(unittest.TestCase):

    def setUp(self):
        sala = Sala("1012", "ICEx", 1)
        self.manha = Disciplina("AAA001", "Manha").obter_turma("TA")
        self.manha.agendar_aula(DiaSemana.SEGUNDA, IntervaloDeHorario.de_texto("07:30", "09:10"), sala, "t")
        self.encostada = Disciplina("AAA002", "Encostada").obter_turma("TA")
        self.encostada.agendar_aula(DiaSemana.SEGUNDA, IntervaloDeHorario.de_texto("09:10", "10:50"), sala, "t")
        self.sobreposta = Disciplina("AAA003", "Sobreposta").obter_turma("TA")
        self.sobreposta.agendar_aula(DiaSemana.SEGUNDA, IntervaloDeHorario.de_texto("09:00", "10:00"), sala, "t")

    def test_turmas_encostadas_nao_conflitam(self):
        grade = GradeDoAluno("ana", "Ana")
        grade.adicionar([self.manha, self.encostada])
        self.assertEqual(2, grade.quantidade)

    def test_conflito_no_pedido_nao_inclui_nenhuma_turma(self):
        grade = GradeDoAluno("ana", "Ana")
        with self.assertRaises(ConflitoDeHorario):
            grade.adicionar([self.encostada, self.sobreposta])
        self.assertEqual(0, grade.quantidade)

    def test_setter_do_nome_valida_e_preserva_o_anterior(self):
        grade = GradeDoAluno("ana", "Ana")
        with self.assertRaises(DadoInvalido):
            grade.nome = " "
        self.assertEqual("Ana", grade.nome)
        grade.nome = "Ana  Clara"
        self.assertEqual("Ana Clara", grade.nome)

    def test_identificador_e_normalizado_e_somente_leitura(self):
        grade = GradeDoAluno("  ANA ", "Ana")
        self.assertEqual("ana", grade.identificador)
        with self.assertRaises(AttributeError):
            grade.identificador = "outra"


if __name__ == "__main__":
    unittest.main()
