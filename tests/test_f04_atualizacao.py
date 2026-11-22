"""F04: atualizar a base de aulas a partir do site do ICEx ou de um arquivo JSON."""

import json
import unittest

import requests

from apoio import REGISTROS_TESTE, TesteComBase, retrato, retrato_banco
from guia_salas.dados import AMOSTRA, FonteIcexArquivo, FonteIcexOnline
from guia_salas.dominio import AtualizacaoRecusada


class SessaoForaDoAr:
    """Substitui a sessão do requests simulando o site do ICEx fora do ar."""

    def get(self, url, **_):
        raise requests.ConnectionError("site fora do ar (simulado)")


def registro(codigo, inicio="07:30", fim="09:10", dias="Seg", sala="1012"):
    """Um item no formato do JSON do ICEx."""
    return {"nome_materia": f"DISCIPLINA {codigo}", "codigo_materia": codigo, "turma": "TA",
            "hora_inicial": inicio, "hora_final": fim, "dia_semana": dias, "nome_sala": sala}


class TestF04Atualizacao(TesteComBase):
    """Estado inicial: base de teste carregada de tests/dados/registros_teste.json (7 disciplinas, 19 aulas, 1 atualização)."""

    def setUp(self):
        super().setUp()
        self.base_antes = retrato_banco(self.sistema.banco)
        self.catalogo_antes = retrato(self.sistema.consulta.catalogo)

    def arquivo(self, conteudo, nome="carga.json"):
        """Grava um JSON de carga na pasta temporária."""
        caminho = self.pasta / nome
        caminho.write_text(json.dumps(conteudo), encoding="utf-8")
        return FonteIcexArquivo(caminho)

    def assert_base_preservada(self):
        self.assertEqual(self.base_antes, retrato_banco(self.sistema.banco))
        self.assertEqual(self.catalogo_antes, retrato(self.sistema.consulta.catalogo))

    def test_c01_carga_valida_substitui_a_base_e_registra_historico(self):
        relatorio = self.sistema.atualizacao.atualizar(FonteIcexArquivo(AMOSTRA))
        self.assertEqual((110, 199, 0), (relatorio.registros_lidos, relatorio.aulas_registradas,
                                         len(relatorio.recusados)))
        self.assertEqual(30, len(self.sistema.consulta.catalogo.disciplinas))
        reaberto = self.reabrir()
        self.assertEqual(199, len(reaberto.consulta.catalogo))
        historico = reaberto.repositorio_aulas.historico()
        self.assertEqual(["arquivo registros_teste.json", "arquivo amostra_icex.json"],
                         [h.origem for h in historico])

    def test_c02_arquivo_inexistente_e_recusado_e_base_preservada(self):
        with self.assertRaises(AtualizacaoRecusada):
            self.sistema.atualizacao.atualizar(FonteIcexArquivo(self.pasta / "nao_existe.json"))
        self.assert_base_preservada()

    def test_c03_site_fora_do_ar_e_recusado_e_base_preservada(self):
        fonte = FonteIcexOnline("https://exemplo.invalido/recupera_salas.php", sessao=SessaoForaDoAr())
        with self.assertRaises(AtualizacaoRecusada):
            self.sistema.atualizacao.atualizar(fonte)
        self.assert_base_preservada()

    def test_c04_carga_sem_aulas_e_recusada(self):
        with self.assertRaises(AtualizacaoRecusada):
            self.sistema.atualizacao.atualizar(self.arquivo({"records": []}))
        self.assert_base_preservada()

    def test_c05_json_em_formato_inesperado_e_recusado(self):
        for conteudo in ({"records": "x"}, {"outra_chave": []}, "texto"):
            with self.assertRaises(AtualizacaoRecusada):
                self.sistema.atualizacao.atualizar(self.arquivo(conteudo))
        arquivo_quebrado = self.pasta / "quebrado.json"
        arquivo_quebrado.write_text("{ nao e json", encoding="utf-8")
        with self.assertRaises(AtualizacaoRecusada):
            self.sistema.atualizacao.atualizar(FonteIcexArquivo(arquivo_quebrado))
        self.assert_base_preservada()

    def test_c06_mais_da_metade_recusada_e_rejeitada(self):
        conteudo = {"records": [registro("AAA001"), registro("AAA002", "11:05", "09:25"),
                                registro("AAA003", "xx", "09:10")]}
        with self.assertRaises(AtualizacaoRecusada) as contexto:
            self.sistema.atualizacao.atualizar(self.arquivo(conteudo))
        self.assertIn("2 de 3 registros foram recusados", str(contexto.exception))
        self.assert_base_preservada()

    def test_c07_metade_exata_recusada_ainda_e_aceita(self):
        conteudo = {"records": [registro("AAA001"), registro("AAA002", "11:05", "09:25")]}
        relatorio = self.sistema.atualizacao.atualizar(self.arquivo(conteudo))
        self.assertEqual((2, 1), (relatorio.registros_lidos, len(relatorio.recusados)))
        self.assertEqual(["AAA001"], [d.codigo for d in self.reabrir().consulta.catalogo.disciplinas])

    def test_c08_falha_ao_gravar_desfaz_tudo(self):
        with self.sistema.banco.transacao() as conexao:
            conexao.execute("CREATE TRIGGER falha BEFORE INSERT ON atualizacao "
                            "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END")
        with self.assertRaises(AtualizacaoRecusada):
            self.sistema.atualizacao.atualizar(FonteIcexArquivo(AMOSTRA))
        self.assert_base_preservada()

    def test_c09_grades_sao_preservadas_e_turma_que_sumiu_fica_pendente(self):
        self.sistema.minha_grade.adicionar("ana", "DCC011 TB; DCC024 TM")
        grades_antes = retrato_banco(self.sistema.banco)["grade_turma"]
        conteudo = json.loads(REGISTROS_TESTE.read_text(encoding="utf-8"))
        conteudo["records"] = [r for r in conteudo["records"] if r["codigo_materia"] != "DCC011"]
        self.sistema.atualizacao.atualizar(self.arquivo(conteudo))
        self.assertEqual(grades_antes, retrato_banco(self.sistema.banco)["grade_turma"])
        grade = self.sistema.minha_grade.abrir("ana")
        self.assertEqual(["DCC024"], [t.disciplina.codigo for t in grade.turmas])
        self.assertEqual({"DCC011": "TB"}, grade.ausentes)

    def test_c10_carga_igual_mantem_os_mesmos_dados(self):
        self.sistema.atualizacao.atualizar(FonteIcexArquivo(REGISTROS_TESTE))
        self.assertEqual(self.catalogo_antes, retrato(self.reabrir().consulta.catalogo))
        self.assertEqual(2, len(self.sistema.repositorio_aulas.historico()))


if __name__ == "__main__":
    unittest.main()
