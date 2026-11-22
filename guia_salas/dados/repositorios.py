"""Gravação e leitura dos dados do Guia de Salas na base SQLite."""

from dataclasses import dataclass
from datetime import datetime

from guia_salas.dados.banco import BancoDeDados


@dataclass(frozen=True)
class RegistroDeAtualizacao:
    """Linha do histórico: quando a base foi trocada, de onde vieram os dados e os totais."""

    momento: str
    origem: str
    registros_lidos: int
    aulas_registradas: int
    registros_recusados: int


@dataclass(frozen=True)
class GradeSalva:
    """Grade como está gravada: identificador, nome e pares (disciplina, turma)."""

    aluno: str
    nome: str
    turmas: list[tuple[str, str]]


class RepositorioDeAulas:
    """Grava o catálogo inteiro numa única transação e guarda o histórico de atualizações."""

    def __init__(self, banco: BancoDeDados):
        """Recebe a base de dados aberta."""
        self._banco = banco

    def quantidade_de_aulas(self) -> int:
        """Número de aulas gravadas."""
        with self._banco.transacao() as conexao:
            return conexao.execute("SELECT COUNT(*) FROM aula").fetchone()[0]

    def substituir(self, catalogo, registro: RegistroDeAtualizacao) -> None:
        """Apaga as aulas gravadas e grava as do catálogo; se algo falhar, nada muda."""
        with self._banco.transacao() as conexao:
            for tabela in ("aula", "turma", "sala", "disciplina"):
                conexao.execute(f"DELETE FROM {tabela}")
            ids_sala = {}
            for sala in catalogo.salas:
                cursor = conexao.execute(
                    "INSERT INTO sala (predio, identificador, andar) VALUES (?, ?, ?)",
                    (sala.predio, sala.identificador, sala.andar))
                ids_sala[sala.chave] = cursor.lastrowid
            for disciplina in catalogo.disciplinas:
                conexao.execute("INSERT INTO disciplina (codigo, nome) VALUES (?, ?)",
                                (disciplina.codigo, disciplina.nome))
                for turma in disciplina.turmas:
                    id_turma = conexao.execute(
                        "INSERT INTO turma (disciplina, codigo) VALUES (?, ?)",
                        (disciplina.codigo, turma.codigo)).lastrowid
                    conexao.executemany(
                        "INSERT INTO aula (turma, sala, dia, inicio, fim, origem) VALUES (?, ?, ?, ?, ?, ?)",
                        [(id_turma, ids_sala[a.sala.chave], a.dia.sigla, f"{a.intervalo.inicio:%H:%M}",
                          f"{a.intervalo.fim:%H:%M}", a.origem) for a in turma.aulas])
            conexao.execute(
                "INSERT INTO atualizacao (momento, origem, registros_lidos, aulas_registradas, "
                "registros_recusados) VALUES (?, ?, ?, ?, ?)",
                (registro.momento, registro.origem, registro.registros_lidos,
                 registro.aulas_registradas, registro.registros_recusados))

    def ultima_atualizacao(self) -> RegistroDeAtualizacao | None:
        """Atualização aceita mais recente, ou None se a base nunca foi preenchida."""
        with self._banco.transacao() as conexao:
            linha = conexao.execute(
                "SELECT momento, origem, registros_lidos, aulas_registradas, registros_recusados "
                "FROM atualizacao ORDER BY id DESC LIMIT 1").fetchone()
        return RegistroDeAtualizacao(*linha) if linha else None

    def historico(self) -> list[RegistroDeAtualizacao]:
        """Todas as atualizações aceitas, da mais antiga para a mais recente."""
        with self._banco.transacao() as conexao:
            linhas = conexao.execute(
                "SELECT momento, origem, registros_lidos, aulas_registradas, registros_recusados "
                "FROM atualizacao ORDER BY id").fetchall()
        return [RegistroDeAtualizacao(*linha) for linha in linhas]

    @staticmethod
    def agora() -> str:
        """Data e hora atuais no formato gravado no histórico."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class RepositorioDeGrades:
    """Grava e lê as grades dos alunos, guardadas pelos códigos de disciplina e turma."""

    def __init__(self, banco: BancoDeDados):
        """Recebe a base de dados aberta."""
        self._banco = banco

    def carregar(self, aluno: str) -> GradeSalva | None:
        """Grade gravada para o identificador, ou None se não existir."""
        with self._banco.transacao() as conexao:
            linha = conexao.execute("SELECT nome FROM grade WHERE aluno = ?", (aluno,)).fetchone()
            if linha is None:
                return None
            turmas = conexao.execute(
                "SELECT disciplina, turma FROM grade_turma WHERE aluno = ? ORDER BY disciplina",
                (aluno,)).fetchall()
        return GradeSalva(aluno, linha[0], [tuple(t) for t in turmas])

    def salvar(self, grade: GradeSalva) -> None:
        """Substitui a grade gravada do aluno numa única transação."""
        with self._banco.transacao() as conexao:
            conexao.execute(
                "INSERT INTO grade (aluno, nome) VALUES (?, ?) "
                "ON CONFLICT(aluno) DO UPDATE SET nome = excluded.nome",
                (grade.aluno, grade.nome))
            conexao.execute("DELETE FROM grade_turma WHERE aluno = ?", (grade.aluno,))
            conexao.executemany(
                "INSERT INTO grade_turma (aluno, disciplina, turma) VALUES (?, ?, ?)",
                [(grade.aluno, disciplina, turma) for disciplina, turma in grade.turmas])

    def alunos(self) -> list[str]:
        """Identificadores com grade gravada."""
        with self._banco.transacao() as conexao:
            return [linha[0] for linha in conexao.execute("SELECT aluno FROM grade ORDER BY aluno")]
