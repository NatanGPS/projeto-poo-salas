"""Montagem do sistema: liga a base de dados, os serviços e as interfaces."""

from dataclasses import dataclass
from pathlib import Path

from guia_salas.dados import (
    AMOSTRA,
    BancoDeDados,
    FonteBancoLocal,
    FonteDeDados,
    FonteIcexArquivo,
    RepositorioDeAulas,
    RepositorioDeGrades,
)
from guia_salas.servicos.atualizacao import ServicoDeAtualizacao
from guia_salas.servicos.atualizador import AtualizadorDeBase, RelatorioDeAtualizacao
from guia_salas.servicos.consulta import ConsultaDeSalas
from guia_salas.servicos.minha_grade import ServicoMinhaGrade
from guia_salas.servicos.planilha import PreenchedorDeGrade

BANCO_PADRAO = Path(__file__).resolve().parent.parent / "base" / "guia_salas.db"
GRADE_DE_EXEMPLO = ("ana", "Ana (exemplo)", "DCC011 TB; MAT038 TB1; MAT001 TA1")


@dataclass(frozen=True)
class Sistema:
    """Objetos compartilhados pelas interfaces: base, repositórios e serviços."""

    banco: BancoDeDados
    repositorio_aulas: RepositorioDeAulas
    consulta: ConsultaDeSalas
    atualizacao: ServicoDeAtualizacao
    minha_grade: ServicoMinhaGrade
    planilha: PreenchedorDeGrade


def abrir_sistema(caminho_banco: Path | str = BANCO_PADRAO) -> Sistema:
    """Abre (ou cria) a base e monta o catálogo com as aulas gravadas nela."""
    banco = BancoDeDados(caminho_banco)
    repositorio_aulas = RepositorioDeAulas(banco)
    catalogo, _ = AtualizadorDeBase([FonteBancoLocal(banco)]).atualizar()
    consulta = ConsultaDeSalas(catalogo)
    return Sistema(
        banco=banco,
        repositorio_aulas=repositorio_aulas,
        consulta=consulta,
        atualizacao=ServicoDeAtualizacao(consulta, repositorio_aulas),
        minha_grade=ServicoMinhaGrade(consulta, RepositorioDeGrades(banco)),
        planilha=PreenchedorDeGrade(consulta),
    )


def preparar_base(sistema: Sistema, fonte: FonteDeDados | None = None,
                  grade_de_exemplo: bool = True) -> RelatorioDeAtualizacao:
    """Preenche a base com a fonte (amostra do ICEx por padrão) e grava a grade fictícia de exemplo."""
    relatorio = sistema.atualizacao.atualizar(fonte or FonteIcexArquivo(AMOSTRA))
    if grade_de_exemplo:
        aluno, nome, pedido = GRADE_DE_EXEMPLO
        grade = sistema.minha_grade.abrir(aluno)
        if grade.quantidade == 0:
            sistema.minha_grade.adicionar(aluno, pedido)
            sistema.minha_grade.renomear(aluno, nome)
    return relatorio
