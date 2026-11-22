"""Verificação manual da F01 (Aula 17) com registros reais do ICEx."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from guia_salas.bot.comandos import ComandosDoBot
from guia_salas.dominio import TermoDeBuscaInvalido
from guia_salas.fontes import FonteIcex
from guia_salas.servicos.atualizador import AtualizadorDeBase
from guia_salas.servicos.catalogo import CatalogoDeAulas
from guia_salas.servicos.consulta import ConsultaDeSalas


class CanalSimulado:
    """Registro local das mensagens que o bot enviaria pelo Telegram."""

    def __init__(self):
        self.mensagens: list[str] = []

    def enviar(self, texto: str) -> None:
        """Guarda a mensagem em vez de enviá-la."""
        self.mensagens.append(texto)


REGISTROS_ICEX = {"records": [
    {"nome_materia": "INTRODUCAO A BANCO DE DADOS", "codigo_materia": "DCC011", "turma": "TE",
     "hora_inicial": "19:00", "hora_final": "20:40", "dia_semana": "Ter-Qui", "nome_sala": "CAD3 - Sala 213"},
    {"nome_materia": "INTRODUCAO A BANCO DE DADOS", "codigo_materia": "DCC011", "turma": "TB",
     "hora_inicial": "09:25", "hora_final": "11:05", "dia_semana": "Seg-Qua", "nome_sala": "2014 - DCC"},
    {"nome_materia": "LINGUAGENS DE PROGRAMACAO", "codigo_materia": "DCC024", "turma": "TM",
     "hora_inicial": "13:00", "hora_final": "14:40", "dia_semana": "Seg-Qua", "nome_sala": "CAD3 - Sala 309"},
    {"nome_materia": "LINGUAGENS DE PROGRAMACAO", "codigo_materia": "DCC024", "turma": "TE",
     "hora_inicial": "19:00", "hora_final": "20:40", "dia_semana": "Seg-Qua", "nome_sala": "2013 - DCC"},
]}


def preparar_catalogo() -> CatalogoDeAulas:
    """Catálogo com DCC011 (turmas TB e TE) e DCC024 (turmas TM e TE), a partir dos registros reais."""
    catalogo = CatalogoDeAulas()
    for registro in FonteIcex.interpretar(REGISTROS_ICEX):
        AtualizadorDeBase.incluir(catalogo, registro)
    return catalogo


def estado(catalogo: CatalogoDeAulas) -> str:
    """Resumo do estado do catálogo: disciplinas, turmas e aulas."""
    turmas = sum(len(d.turmas) for d in catalogo.disciplinas)
    return f"{len(catalogo.disciplinas)} disciplinas, {turmas} turmas, {len(catalogo)} aulas"


def cabecalho(titulo: str) -> None:
    print("=" * 72)
    print(titulo)
    print("=" * 72)


def comparar(rotulo: str, esperado, observado) -> bool:
    """Imprime esperado e observado lado a lado."""
    confere = esperado == observado
    print(f"  {rotulo}")
    print(f"    esperado:  {esperado}")
    print(f"    observado: {observado}")
    print(f"    confere:   {'sim' if confere else 'NÃO'}")
    return confere


def cenario_c01() -> bool:
    """F01-C01: buscar 'banco de dados' com a disciplina cadastrada."""
    cabecalho("F01-C01: Válido: /sala banco de dados com DCC011 cadastrada")
    catalogo = preparar_catalogo()
    consulta = ConsultaDeSalas(catalogo)
    canal = CanalSimulado()
    antes = estado(catalogo)
    print(f"Estado inicial: {antes}; mensagens enviadas: {len(canal.mensagens)}")

    resultado = consulta.buscar_por_disciplina("banco de dados")
    canal.enviar(ComandosDoBot(consulta).sala("banco de dados"))

    aulas = [(a.turma.codigo, a.dia.sigla, str(a.intervalo), a.sala.predio, a.sala.identificador)
             for d in resultado.disciplinas for a in d.aulas()]
    ok = all([
        comparar("disciplinas encontradas", ["DCC011"], [d.codigo for d in resultado.disciplinas]),
        comparar("aulas (turma, dia, horário, prédio, sala)", [
            ("TB", "SEG", "09:25-11:05", "ICEx", "2014 - DCC"), ("TB", "QUA", "09:25-11:05", "ICEx", "2014 - DCC"),
            ("TE", "TER", "19:00-20:40", "CAD3", "213"), ("TE", "QUI", "19:00-20:40", "CAD3", "213"),
        ], aulas),
        comparar("mensagens enviadas", 1, len(canal.mensagens)),
        comparar("estado do catálogo (inalterado)", antes, estado(catalogo)),
    ])
    print("Mensagem registrada:\n" + "\n".join("  | " + l for l in canal.mensagens[0].splitlines()))
    return ok


def cenario_c02() -> bool:
    """F01-C02: termo com 1 caractere é rejeitado sem consultar resultados."""
    cabecalho("F01-C02: Inválido: /sala C (termo com menos de 3 caracteres)")
    catalogo = preparar_catalogo()
    consulta = ConsultaDeSalas(catalogo)
    canal = CanalSimulado()
    antes = estado(catalogo)
    print(f"Estado inicial: {antes}; mensagens enviadas: {len(canal.mensagens)}")

    excecao = None
    try:
        consulta.buscar_por_disciplina("  C ")
    except TermoDeBuscaInvalido as erro:
        excecao = type(erro).__name__
    canal.enviar(ComandosDoBot(consulta).sala("  C "))

    ok = all([
        comparar("exceção lançada pela consulta", "TermoDeBuscaInvalido", excecao),
        comparar("mensagem é a orientação de uso", True,
                 canal.mensagens[0].startswith("Informe ao menos 3 caracteres")),
        comparar("mensagens enviadas", 1, len(canal.mensagens)),
        comparar("estado do catálogo (inalterado)", antes, estado(catalogo)),
    ])
    print("Mensagem registrada:\n" + "\n".join("  | " + l for l in canal.mensagens[0].splitlines()))
    return ok


def cenario_c03() -> bool:
    """F01-C03: termo válido de disciplina que não consta no quadro do ICEx."""
    cabecalho("F01-C03: Limite: /sala Programação Orientada a Objetos (nenhum resultado)")
    catalogo = preparar_catalogo()
    consulta = ConsultaDeSalas(catalogo)
    canal = CanalSimulado()
    antes = estado(catalogo)
    print(f"Estado inicial: {antes}; mensagens enviadas: {len(canal.mensagens)}")

    resultado = consulta.buscar_por_disciplina("Programação Orientada a Objetos")
    canal.enviar(ComandosDoBot(consulta).sala("Programação Orientada a Objetos"))

    ok = all([
        comparar("resultado encontrou algo?", False, resultado.encontrou),
        comparar("disciplinas encontradas", [], [d.codigo for d in resultado.disciplinas]),
        comparar("mensagem informa que não encontrou", True,
                 canal.mensagens[0].startswith(
                     'Nenhuma disciplina encontrada para "Programação Orientada a Objetos"')),
        comparar("mensagens enviadas", 1, len(canal.mensagens)),
        comparar("estado do catálogo (inalterado)", antes, estado(catalogo)),
    ])
    print("Mensagem registrada:\n" + "\n".join("  | " + l for l in canal.mensagens[0].splitlines()))
    return ok


if __name__ == "__main__":
    resultados = {"F01-C01": cenario_c01(), "F01-C02": cenario_c02(), "F01-C03": cenario_c03()}
    cabecalho("Resumo")
    for nome, ok in resultados.items():
        print(f"  {nome}: {'observado confere com o esperado' if ok else 'DIVERGENTE'}")
