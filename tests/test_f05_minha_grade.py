"""F05: salvar, consultar e remover turmas na grade do aluno."""

import unittest

from apoio import REGISTROS_GRADE_CHEIA, TesteComBase, retrato_banco
from guia_salas.apresentacao.comandos import ComandosDoBot
from guia_salas.dominio import (
    ConflitoDeHorario,
    DadoInvalido,
    Duplicidade,
    GravacaoFalhou,
    LimiteExcedido,
    NaoEncontrado,
)


def conteudo(grade) -> list[tuple[str, str]]:
    """Pares (disciplina, turma) da grade."""
    return [(t.disciplina.codigo, t.codigo) for t in grade.turmas]


class TestF05MinhaGrade(TesteComBase):
    """Estado inicial: base de teste com os registros de tests/dados; a grade "ana" tem DCC011 TB (seg e qua, 09:25-11:05)."""

    def setUp(self):
        super().setUp()
        self.servico = self.sistema.minha_grade
        self.servico.adicionar("ana", "DCC011 TB")
        self.antes = retrato_banco(self.sistema.banco)

    def assert_nada_mudou(self):
        self.assertEqual(self.antes, retrato_banco(self.sistema.banco))
        self.assertEqual([("DCC011", "TB")], conteudo(self.servico.abrir("ana")))

    def test_c01_adiciona_turma_e_grava(self):
        turmas = self.servico.adicionar("ana", "dcc024 tm")
        self.assertEqual([("DCC024", "TM")], [(t.disciplina.codigo, t.codigo) for t in turmas])
        reaberta = self.reabrir().minha_grade.abrir("ana")
        self.assertEqual([("DCC011", "TB"), ("DCC024", "TM")], conteudo(reaberta))

    def test_c02_adiciona_varias_turmas_num_pedido(self):
        self.servico.adicionar("ana", "DCC024 TM; MAT038 TB1, MAT001 TOL1")
        self.assertEqual([("DCC011", "TB"), ("DCC024", "TM"), ("MAT001", "TOL1"), ("MAT038", "TB1")],
                         conteudo(self.servico.abrir("ana")))

    def test_c03_conflito_com_turma_salva_e_recusado(self):
        with self.assertRaises(ConflitoDeHorario):
            self.servico.adicionar("ana", "DCC001 TB")
        self.assert_nada_mudou()

    def test_c04_conflito_no_pedido_recusa_todas_as_turmas(self):
        with self.assertRaises(ConflitoDeHorario):
            self.servico.adicionar("outro", "DCC024 TM; DCC001 TB; DCC011 TB")
        self.assertEqual(0, self.servico.abrir("outro").quantidade)
        self.assert_nada_mudou()

    def test_c05_disciplina_inexistente_recusa_o_pedido_inteiro(self):
        with self.assertRaises(NaoEncontrado):
            self.servico.adicionar("ana", "DCC024 TM; XYZ999 TA")
        self.assert_nada_mudou()

    def test_c06_turma_inexistente_e_recusada_com_as_turmas_validas(self):
        with self.assertRaises(NaoEncontrado) as contexto:
            self.servico.adicionar("ana", "DCC024 TZ")
        self.assertIn("Turmas existentes: TE, TM", str(contexto.exception))
        self.assert_nada_mudou()

    def test_c07_disciplina_ja_na_grade_e_recusada(self):
        with self.assertRaises(Duplicidade):
            self.servico.adicionar("ana", "DCC011 TE")
        self.assert_nada_mudou()

    def test_c08_disciplina_repetida_no_pedido_e_recusada(self):
        with self.assertRaises(Duplicidade):
            self.servico.adicionar("outro", "DCC024 TM; DCC024 TE")
        self.assert_nada_mudou()

    def test_c09_pedido_mal_formatado_e_recusado(self):
        for pedido in ("", "  ;  ", "DCC024", "DCC024 TM extra"):
            with self.assertRaises(DadoInvalido):
                self.servico.adicionar("ana", pedido)
        self.assert_nada_mudou()

    def test_c10_remove_disciplina_e_grava(self):
        self.assertEqual("DCC011", self.servico.remover("ana", " dcc011 "))
        self.assertEqual(0, self.reabrir().minha_grade.abrir("ana").quantidade)

    def test_c11_remover_disciplina_fora_da_grade_e_recusado(self):
        with self.assertRaises(NaoEncontrado):
            self.servico.remover("ana", "DCC024")
        self.assert_nada_mudou()

    def test_c12_nome_valido_e_alterado_pelo_setter(self):
        self.servico.renomear("ana", "  Ana   Souza ")
        self.assertEqual("Ana Souza", self.reabrir().minha_grade.abrir("ana").nome)
        self.servico.renomear("ana", "x" * 40)
        self.assertEqual(40, len(self.servico.abrir("ana").nome))

    def test_c13_nome_vazio_ou_longo_e_recusado(self):
        for nome in ("", "   ", "x" * 41):
            with self.assertRaises(DadoInvalido):
                self.servico.renomear("ana", nome)
        self.assert_nada_mudou()

    def test_c14_identificacao_invalida_e_recusada(self):
        for aluno in ("", "a", "Ana Maria", "joão", "x" * 41):
            with self.assertRaises(DadoInvalido):
                self.servico.adicionar(aluno, "DCC024 TM")
        self.assert_nada_mudou()

    def test_c15_falha_ao_gravar_preserva_a_grade(self):
        with self.sistema.banco.transacao() as conexao:
            conexao.execute("CREATE TRIGGER falha BEFORE INSERT ON grade_turma "
                            "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END")
        with self.assertRaises(GravacaoFalhou):
            self.servico.adicionar("ana", "DCC024 TM")
        self.assert_nada_mudou()


class TestF05LimiteDaGrade(TesteComBase):
    """Estado inicial: base de teste com tests/dados/registros_grade_cheia.json (9 disciplinas fictícias sem conflito)."""

    REGISTROS = REGISTROS_GRADE_CHEIA

    def test_c16_oito_disciplinas_sao_aceitas_e_a_nona_e_recusada(self):
        servico = self.sistema.minha_grade
        servico.adicionar("bia", "; ".join(f"TST00{i} TA" for i in range(1, 9)))
        self.assertEqual(8, servico.abrir("bia").quantidade)
        antes = retrato_banco(self.sistema.banco)
        with self.assertRaises(LimiteExcedido):
            servico.adicionar("bia", "TST009 TA")
        self.assertEqual(antes, retrato_banco(self.sistema.banco))

    def test_c17_pedido_com_nove_disciplinas_e_recusado(self):
        with self.assertRaises(DadoInvalido):
            self.sistema.minha_grade.adicionar("bia", "; ".join(f"TST00{i} TA" for i in range(1, 10)))
        self.assertEqual(0, self.sistema.minha_grade.abrir("bia").quantidade)


class TestF05ComandosDoBot(TesteComBase):
    """Estado inicial: base de teste com os registros de tests/dados; a conversa 42 não tem grade."""

    def setUp(self):
        super().setUp()
        self.comandos = ComandosDoBot(self.sistema)
        self.aluno = ComandosDoBot.aluno_do_chat(42)

    def test_c18_fluxo_adicionar_ver_e_remover(self):
        self.assertIn("A grade está vazia", self.comandos.minha_grade(self.aluno))
        self.assertEqual("Adicionada(s) à grade: DCC011 TB, DCC024 TM.",
                         self.comandos.adicionar(self.aluno, "DCC011 TB; DCC024 TM"))
        grade = self.comandos.minha_grade(self.aluno)
        self.assertIn("Grade: Minha grade (2 disciplina(s))", grade)
        self.assertIn("09:25-11:05 DCC011 TB, sala 2014 - DCC (ICEx, 2º andar)", grade)
        self.assertEqual("DCC011 removida da grade.", self.comandos.remover(self.aluno, "DCC011"))

    def test_c19_recusa_no_bot_informa_que_nada_mudou(self):
        self.comandos.adicionar(self.aluno, "DCC011 TB")
        resposta = self.comandos.adicionar(self.aluno, "DCC001 TB")
        self.assertTrue(resposta.startswith("Nada foi alterado."))
        self.assertIn("conflita", resposta)
        self.assertTrue(self.comandos.remover(self.aluno, "").startswith("Uso: /remover"))


if __name__ == "__main__":
    unittest.main()
