"""Base de dados SQLite do Guia de Salas."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS disciplina (
    codigo TEXT PRIMARY KEY,
    nome   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS turma (
    id         INTEGER PRIMARY KEY,
    disciplina TEXT NOT NULL REFERENCES disciplina(codigo),
    codigo     TEXT NOT NULL,
    UNIQUE (disciplina, codigo)
);
CREATE TABLE IF NOT EXISTS sala (
    id            INTEGER PRIMARY KEY,
    predio        TEXT NOT NULL,
    identificador TEXT NOT NULL,
    andar         INTEGER,
    UNIQUE (predio, identificador)
);
CREATE TABLE IF NOT EXISTS aula (
    id     INTEGER PRIMARY KEY,
    turma  INTEGER NOT NULL REFERENCES turma(id),
    sala   INTEGER NOT NULL REFERENCES sala(id),
    dia    TEXT NOT NULL,
    inicio TEXT NOT NULL,
    fim    TEXT NOT NULL,
    origem TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS atualizacao (
    id                  INTEGER PRIMARY KEY,
    momento             TEXT NOT NULL,
    origem              TEXT NOT NULL,
    registros_lidos     INTEGER NOT NULL,
    aulas_registradas   INTEGER NOT NULL,
    registros_recusados INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS grade (
    aluno TEXT PRIMARY KEY,
    nome  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS grade_turma (
    aluno      TEXT NOT NULL REFERENCES grade(aluno) ON DELETE CASCADE,
    disciplina TEXT NOT NULL,
    turma      TEXT NOT NULL,
    PRIMARY KEY (aluno, disciplina)
);
"""


class FalhaNaBase(Exception):
    """Erro do SQLite ao ler ou gravar; a transação em andamento foi desfeita."""


class BancoDeDados:
    """Arquivo SQLite com as tabelas de aulas, histórico de atualizações e grades dos alunos."""

    def __init__(self, caminho: Path | str):
        """Guarda o caminho do arquivo e cria as tabelas que ainda não existem."""
        self._caminho = Path(caminho)
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.transacao() as conexao:
            conexao.executescript(ESQUEMA)

    @property
    def caminho(self) -> Path:
        """Arquivo .db usado."""
        return self._caminho

    @contextmanager
    def transacao(self) -> Iterator[sqlite3.Connection]:
        """Abre uma conexão; confirma tudo ao final ou desfaz tudo se ocorrer uma exceção."""
        try:
            conexao = sqlite3.connect(self._caminho)
        except sqlite3.Error as erro:
            raise FalhaNaBase(f"Não foi possível abrir {self._caminho}: {erro}") from erro
        try:
            conexao.execute("PRAGMA foreign_keys = ON")
            with conexao:
                yield conexao
        except sqlite3.Error as erro:
            raise FalhaNaBase(str(erro)) from erro
        finally:
            conexao.close()
