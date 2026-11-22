"""Grade de turmas que um aluno escolheu acompanhar."""

import re

from guia_salas.dominio.aula import Aula
from guia_salas.dominio.erros import (
    ConflitoDeHorario,
    DadoInvalido,
    Duplicidade,
    LimiteExcedido,
    NaoEncontrado,
)
from guia_salas.dominio.turma import Turma

LIMITE_DE_DISCIPLINAS = 8
TAMANHO_MAXIMO_DO_NOME = 40
FORMATO_DO_IDENTIFICADOR = re.compile(r"[a-z0-9][a-z0-9._:-]{1,39}")


class GradeDoAluno:
    """Turmas escolhidas por um aluno, no máximo uma por disciplina e sem conflito de horário."""

    def __init__(self, identificador: str, nome: str):
        """Valida o identificador (2 a 40 letras, dígitos, ponto, hífen, sublinhado ou dois-pontos) e o nome."""
        identificador = identificador.strip().lower()
        if not FORMATO_DO_IDENTIFICADOR.fullmatch(identificador):
            raise DadoInvalido(
                "Identificação inválida. Use de 2 a 40 letras sem acento, números, ponto, hífen ou sublinhado."
            )
        self._identificador = identificador
        self._nome = ""
        self.nome = nome
        self._turmas: dict[str, Turma] = {}
        self._ausentes: dict[str, str] = {}

    @property
    def identificador(self) -> str:
        """Chave da grade na base: um apelido no terminal ou telegram:<id> no bot."""
        return self._identificador

    @property
    def nome(self) -> str:
        """Nome exibido no cabeçalho da grade."""
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        """Aceita de 1 a 40 caracteres, com espaços extras removidos."""
        valor = " ".join(str(valor).split())
        if not valor:
            raise DadoInvalido("O nome da grade não pode ficar vazio.")
        if len(valor) > TAMANHO_MAXIMO_DO_NOME:
            raise DadoInvalido(f"O nome da grade pode ter no máximo {TAMANHO_MAXIMO_DO_NOME} caracteres.")
        self._nome = valor

    @property
    def turmas(self) -> list[Turma]:
        """Turmas da grade ordenadas pelo código da disciplina."""
        return [self._turmas[c] for c in sorted(self._turmas)]

    @property
    def ausentes(self) -> dict[str, str]:
        """Disciplina e turma salvas que não existem na base atual (cópia)."""
        return dict(sorted(self._ausentes.items()))

    @property
    def quantidade(self) -> int:
        """Total de disciplinas na grade, inclusive as ausentes da base."""
        return len(self._turmas) + len(self._ausentes)

    def aulas(self) -> list[Aula]:
        """Aulas de todas as turmas, ordenadas por dia e horário."""
        todas = [aula for turma in self._turmas.values() for aula in turma.aulas]
        return sorted(todas, key=lambda a: (a.dia.numero, a.intervalo.inicio, a.disciplina.codigo))

    def contem(self, codigo_disciplina: str) -> bool:
        """Indica se a disciplina está na grade."""
        codigo = "".join(codigo_disciplina.split()).upper()
        return codigo in self._turmas or codigo in self._ausentes

    def adicionar(self, turmas: list[Turma]) -> None:
        """Inclui todas as turmas ou nenhuma: recusa repetição, limite excedido e conflito de horário."""
        if not turmas:
            raise DadoInvalido("Nenhuma turma informada.")
        codigos = [t.disciplina.codigo for t in turmas]
        repetidos = sorted({c for c in codigos if codigos.count(c) > 1})
        if repetidos:
            raise Duplicidade(f"Disciplina repetida no pedido: {', '.join(repetidos)}.")
        for turma in turmas:
            if self.contem(turma.disciplina.codigo):
                atual = self._turmas.get(turma.disciplina.codigo)
                complemento = f" (turma {atual.codigo})" if atual else ""
                raise Duplicidade(
                    f"{turma.disciplina.codigo} já está na grade{complemento}. Remova antes de trocar de turma."
                )
        if self.quantidade + len(turmas) > LIMITE_DE_DISCIPLINAS:
            raise LimiteExcedido(
                f"A grade aceita no máximo {LIMITE_DE_DISCIPLINAS} disciplinas; "
                f"já tem {self.quantidade} e o pedido traz {len(turmas)}."
            )
        self._verificar_conflitos(list(self._turmas.values()) + list(turmas))
        for turma in turmas:
            self._turmas[turma.disciplina.codigo] = turma

    def remover(self, codigo_disciplina: str) -> str:
        """Retira a disciplina da grade e devolve o código removido."""
        codigo = "".join(codigo_disciplina.split()).upper()
        if not self.contem(codigo):
            raise NaoEncontrado(f"{codigo or 'A disciplina'} não está na grade.")
        self._turmas.pop(codigo, None)
        self._ausentes.pop(codigo, None)
        return codigo

    def restaurar(self, turmas: list[Turma], ausentes: dict[str, str]) -> None:
        """Recoloca o conteúdo salvo na base, sem repetir as verificações de inclusão."""
        self._turmas = {t.disciplina.codigo: t for t in turmas}
        self._ausentes = dict(ausentes)

    @staticmethod
    def _verificar_conflitos(turmas: list[Turma]) -> None:
        """Lança ConflitoDeHorario se duas turmas diferentes tiverem aulas sobrepostas no mesmo dia."""
        aulas = [aula for turma in turmas for aula in turma.aulas]
        for i, primeira in enumerate(aulas):
            for segunda in aulas[i + 1:]:
                if (primeira.turma is not segunda.turma and primeira.dia == segunda.dia
                        and primeira.intervalo.sobrepoe(segunda.intervalo)):
                    raise ConflitoDeHorario(
                        f"{primeira.disciplina.codigo} {primeira.turma.codigo} ({primeira.dia} "
                        f"{primeira.intervalo}) conflita com {segunda.disciplina.codigo} "
                        f"{segunda.turma.codigo} ({segunda.dia} {segunda.intervalo})."
                    )

    def __str__(self) -> str:
        return f"Grade {self._nome} ({self._identificador})"
