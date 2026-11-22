"""F05: grade de turmas salva pelo aluno."""

import re

from guia_salas.dados import FalhaNaBase, GradeSalva, RepositorioDeGrades
from guia_salas.dominio import (
    LIMITE_DE_DISCIPLINAS,
    DadoInvalido,
    GradeDoAluno,
    GravacaoFalhou,
    NaoEncontrado,
    Turma,
)
from guia_salas.servicos.consulta import ConsultaDeSalas


class ServicoMinhaGrade:
    """Abre a grade gravada, aplica a operação pedida pelas regras de GradeDoAluno e grava o resultado."""

    def __init__(self, consulta: ConsultaDeSalas, repositorio: RepositorioDeGrades):
        """Recebe a consulta (para achar as turmas no catálogo atual) e o repositório de grades."""
        self._consulta = consulta
        self._repositorio = repositorio

    def abrir(self, aluno: str, nome_padrao: str | None = None) -> GradeDoAluno:
        """Grade gravada do aluno, ou uma grade vazia ainda não gravada."""
        grade = GradeDoAluno(aluno, nome_padrao or aluno)
        try:
            salva = self._repositorio.carregar(grade.identificador)
        except FalhaNaBase as erro:
            raise GravacaoFalhou(f"Não foi possível ler a grade: {erro}.") from erro
        if salva is None:
            return grade
        grade.nome = salva.nome
        turmas, ausentes = [], {}
        for codigo, turma in salva.turmas:
            try:
                turmas.append(self._consulta.catalogo.turma(codigo, turma))
            except NaoEncontrado:
                ausentes[codigo] = turma
        grade.restaurar(turmas, ausentes)
        return grade

    def adicionar(self, aluno: str, pedido: str, nome_padrao: str | None = None) -> list[Turma]:
        """Inclui as turmas do pedido ("DCC011 TB; MAT001 TA1"): todas são gravadas ou nenhuma."""
        grade = self.abrir(aluno, nome_padrao)
        turmas = [self._consulta.catalogo.turma(codigo, turma) for codigo, turma in self.ler_pedido(pedido)]
        grade.adicionar(turmas)
        self._gravar(grade)
        return turmas

    def remover(self, aluno: str, codigo_disciplina: str) -> str:
        """Retira uma disciplina da grade gravada e devolve o código removido."""
        grade = self.abrir(aluno)
        codigo = grade.remover(codigo_disciplina)
        self._gravar(grade)
        return codigo

    def renomear(self, aluno: str, nome: str) -> GradeDoAluno:
        """Altera o nome exibido da grade pelo setter e grava."""
        grade = self.abrir(aluno)
        grade.nome = nome
        self._gravar(grade)
        return grade

    @staticmethod
    def ler_pedido(pedido: str) -> list[tuple[str, str]]:
        """Converte "DCC011 TB; MAT001 TA1" em pares (disciplina, turma); separa por ponto e vírgula, vírgula ou linha."""
        itens = [i.strip() for i in re.split(r"[;,\n]+", pedido) if i.strip()]
        if not itens:
            raise DadoInvalido("Informe ao menos uma disciplina e turma, como DCC011 TB.")
        if len(itens) > LIMITE_DE_DISCIPLINAS:
            raise DadoInvalido(f"Um pedido pode ter no máximo {LIMITE_DE_DISCIPLINAS} disciplinas.")
        pares = []
        for item in itens:
            partes = item.split()
            if len(partes) != 2:
                raise DadoInvalido(f"\"{item}\" não está no formato CÓDIGO TURMA, como DCC011 TB.")
            pares.append((partes[0].upper(), partes[1].upper()))
        return pares

    def _gravar(self, grade: GradeDoAluno) -> None:
        """Grava as turmas encontradas e as ausentes, para não perder o que sumiu da base."""
        pares = [(t.disciplina.codigo, t.codigo) for t in grade.turmas] + list(grade.ausentes.items())
        try:
            self._repositorio.salvar(GradeSalva(grade.identificador, grade.nome, sorted(pares)))
        except FalhaNaBase as erro:
            raise GravacaoFalhou(f"Não foi possível gravar a grade: {erro}. Nada foi alterado.") from erro
