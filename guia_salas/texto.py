"""Funções de normalização de texto usadas nas buscas."""

import re
import unicodedata

ROMANOS = {
    "1": "i", "2": "ii", "3": "iii", "4": "iv", "5": "v",
    "6": "vi", "7": "vii", "8": "viii", "9": "ix",
}


def normalizar(texto: str) -> str:
    """Remove acentos, converte para minúsculas e compacta espaços."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return " ".join(sem_acento.lower().split())


def palavras(texto: str) -> list[str]:
    """Divide o texto normalizado em palavras, trocando algarismos 1-9 por romanos."""
    tokens = re.findall(r"[a-z0-9]+", normalizar(texto))
    return [ROMANOS.get(t, t) for t in tokens]
