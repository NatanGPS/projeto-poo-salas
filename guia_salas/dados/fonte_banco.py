"""Fonte que lê as aulas já gravadas na base SQLite."""

from guia_salas.dados.banco import BancoDeDados, FalhaNaBase
from guia_salas.dados.fonte_base import FonteDeDados, FonteIndisponivel, RegistroDeAula

CONSULTA_AULAS = """
SELECT d.codigo, d.nome, t.codigo, a.dia, a.inicio, a.fim, s.identificador, s.predio, s.andar, a.origem
FROM aula a
JOIN turma t ON t.id = a.turma
JOIN disciplina d ON d.codigo = t.disciplina
JOIN sala s ON s.id = a.sala
ORDER BY a.id
"""


class FonteBancoLocal(FonteDeDados):
    """Lê da base local os registros gravados na última atualização aceita."""

    def __init__(self, banco: BancoDeDados):
        """Recebe a base de dados aberta."""
        self._banco = banco

    @property
    def nome(self) -> str:
        """Nome da fonte."""
        return "Base local"

    @property
    def descricao(self) -> str:
        """Arquivo da base."""
        return f"base local ({self._banco.caminho.name})"

    def coletar(self) -> list[RegistroDeAula]:
        """Devolve um registro por aula gravada, com o dia como sigla (SEG, TER...)."""
        try:
            with self._banco.transacao() as conexao:
                linhas = conexao.execute(CONSULTA_AULAS).fetchall()
        except FalhaNaBase as erro:
            raise FonteIndisponivel(f"Falha ao ler a base local: {erro}") from erro
        return [
            RegistroDeAula(codigo=codigo, nome=nome, turma=turma, dias=dia, inicio=inicio, fim=fim,
                           sala=sala, predio=predio, andar=andar, origem=origem)
            for codigo, nome, turma, dia, inicio, fim, sala, predio, andar, origem in linhas
        ]
