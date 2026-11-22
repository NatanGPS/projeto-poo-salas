"""Intervalo de horário de uma aula."""

from dataclasses import dataclass
from datetime import time

from guia_salas.dominio.erros import DadoInvalido


@dataclass(frozen=True)
class IntervaloDeHorario:
    """Período entre um horário de início e um de fim, no mesmo dia."""

    inicio: time
    fim: time

    def __post_init__(self):
        if self.inicio >= self.fim:
            raise DadoInvalido(
                f"Início ({self.inicio:%H:%M}) deve ser anterior ao fim ({self.fim:%H:%M})."
            )

    @classmethod
    def de_texto(cls, inicio: str, fim: str) -> "IntervaloDeHorario":
        """Cria o intervalo a partir de textos no formato HH:MM ou HHhMM."""
        return cls(ler_hora(inicio), ler_hora(fim))

    def contem(self, instante: time) -> bool:
        """Indica se o instante está dentro do intervalo (fim exclusivo)."""
        return self.inicio <= instante < self.fim

    def sobrepoe(self, outro: "IntervaloDeHorario") -> bool:
        """Indica se os dois intervalos têm algum trecho em comum."""
        return self.inicio < outro.fim and outro.inicio < self.fim

    def __str__(self) -> str:
        return f"{self.inicio:%H:%M}-{self.fim:%H:%M}"


def ler_hora(texto: str) -> time:
    """Converte '7:30', '07:30' ou '07h30' em time."""
    limpo = texto.strip().lower().replace("h", ":")
    if limpo.endswith(":"):
        limpo += "00"
    try:
        horas, minutos = limpo.split(":")
        return time(int(horas), int(minutos))
    except ValueError as erro:
        raise DadoInvalido(f"Horário inválido: {texto!r}") from erro
