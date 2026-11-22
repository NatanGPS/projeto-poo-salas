"""Disciplina oferecida no semestre."""

from guia_salas.dominio.aula import Aula
from guia_salas.dominio.erros import DadoInvalido
from guia_salas.dominio.turma import Turma
from guia_salas.texto import palavras


class Disciplina:
    """Disciplina identificada por código, com uma ou mais turmas."""

    def __init__(self, codigo: str, nome: str):
        """Valida código e nome não vazios; o código é guardado sem espaços e em maiúsculas."""
        codigo = "".join(codigo.split()).upper()
        nome = " ".join(nome.split())
        if not codigo:
            raise DadoInvalido("A disciplina precisa de um código.")
        if not nome:
            raise DadoInvalido("A disciplina precisa de um nome.")
        self._codigo = codigo
        self._nome = nome
        self._turmas: dict[str, Turma] = {}

    @property
    def codigo(self) -> str:
        """Código único da disciplina, como DCC011."""
        return self._codigo

    @property
    def nome(self) -> str:
        """Nome da disciplina como aparece na fonte."""
        return self._nome

    @property
    def turmas(self) -> list[Turma]:
        """Turmas ordenadas pelo código."""
        return [self._turmas[c] for c in sorted(self._turmas)]

    def obter_turma(self, codigo: str) -> Turma:
        """Devolve a turma com o código informado, criando-a se ainda não existir."""
        chave = "".join(codigo.split()).upper()
        if chave not in self._turmas:
            self._turmas[chave] = Turma(chave, self)
        return self._turmas[chave]

    def aulas(self) -> list[Aula]:
        """Todas as aulas de todas as turmas da disciplina."""
        return [aula for turma in self.turmas for aula in turma.aulas]

    def corresponde(self, termo: str) -> bool:
        """Indica se o termo é o código da disciplina ou se todas as suas palavras iniciam palavras do nome."""
        if "".join(termo.split()).upper() == self._codigo:
            return True
        do_nome = palavras(self._nome)
        do_termo = palavras(termo)
        return bool(do_termo) and all(
            any(p == t or (len(t) >= 3 and p.startswith(t)) for p in do_nome)
            for t in do_termo
        )

    def __str__(self) -> str:
        return f"{self._codigo} - {self._nome}"

    def __repr__(self) -> str:
        return f"Disciplina({self._codigo!r}, {self._nome!r})"


