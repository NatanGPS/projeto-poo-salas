"""Cadastro em memória das disciplinas, salas e aulas consolidadas."""

from datetime import time

from guia_salas.dominio import (
    Aula,
    DiaSemana,
    Disciplina,
    IntervaloDeHorario,
    Sala,
)


class CatalogoDeAulas:
    """Disciplinas (_disciplinas) e salas (_salas) carregadas em memória."""

    def __init__(self):
        """Cria o catálogo vazio."""
        self._disciplinas: dict[str, Disciplina] = {}
        self._salas: dict[tuple[str, str], Sala] = {}

    @property
    def disciplinas(self) -> list[Disciplina]:
        """Disciplinas ordenadas pelo código."""
        return [self._disciplinas[c] for c in sorted(self._disciplinas)]

    @property
    def salas(self) -> list[Sala]:
        """Salas ordenadas por prédio, andar e identificador."""
        return sorted(self._salas.values(), key=lambda s: (s.predio, s.andar or 0, s.identificador))

    @property
    def predios(self) -> list[str]:
        """Nomes dos prédios com salas presenciais na base."""
        return sorted({s.predio for s in self._salas.values() if s.presencial})

    def aulas(self) -> list[Aula]:
        """Todas as aulas registradas."""
        return [aula for d in self.disciplinas for aula in d.aulas()]

    def disciplina_por_codigo(self, codigo: str) -> Disciplina | None:
        """Devolve a disciplina com o código informado, se existir."""
        return self._disciplinas.get("".join(codigo.split()).upper())

    def obter_sala(self, identificador: str, predio: str, andar: int | None) -> Sala:
        """Devolve a sala cadastrada com essa chave, criando-a se necessário."""
        nova = Sala(identificador, predio, andar)
        return self._salas.setdefault(nova.chave, nova)

    def registrar_aula(self, codigo: str, nome: str, turma: str, dia: DiaSemana,
                       intervalo: IntervaloDeHorario, sala: Sala, origem: str) -> Aula:
        """Registra uma aula; turmas diferentes podem dividir a mesma sala e horário (turmas conjuntas)."""
        sala = self._salas.get(sala.chave, sala)
        chave = "".join(codigo.split()).upper()
        disciplina = self._disciplinas.get(chave) or Disciplina(codigo, nome)
        aula = disciplina.obter_turma(turma).agendar_aula(dia, intervalo, sala, origem)
        self._salas.setdefault(sala.chave, sala)
        self._disciplinas.setdefault(disciplina.codigo, disciplina)
        return aula

    def turmas_na_sala(self, sala: Sala, dia: DiaSemana, intervalo: IntervaloDeHorario) -> list[Aula]:
        """Aulas que ocupam a sala no dia, em horário sobreposto ao intervalo."""
        return [a for a in self.aulas()
                if a.sala == sala and a.dia == dia and a.intervalo.sobrepoe(intervalo)]

    def buscar_disciplinas(self, termo: str) -> list[Disciplina]:
        """Disciplinas cujo código ou nome correspondem ao termo, sem alterar o catálogo."""
        exata = self.disciplina_por_codigo(termo)
        if exata:
            return [exata]
        return [d for d in self.disciplinas if d.corresponde(termo)]

    def salas_livres(self, dia: DiaSemana, instante: time, andar: int | None = None,
                     predio: str | None = None) -> list[Sala]:
        """Salas conhecidas sem aula no dia e instante, com filtro opcional de andar e prédio."""
        aulas = self.aulas()
        return [
            sala for sala in self.salas
            if sala.presencial
            and (andar is None or sala.andar == andar)
            and (predio is None or sala.predio.lower() == predio.lower())
            and sala.esta_livre(dia, instante, aulas)
        ]

    def __len__(self) -> int:
        return len(self.aulas())
