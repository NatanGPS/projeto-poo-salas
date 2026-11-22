"""Baixa o JSON de aulas do ICEx e salva uma cópia local."""

import json
import sys
from collections import Counter
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from guia_salas.dados import URL_DADOS, FonteIcex, FonteIcexArquivo
from guia_salas.servicos.atualizador import AtualizadorDeBase


def main() -> None:
    """Baixa, salva e resume os dados do ICEx."""
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else "dados_icex.json")
    resposta = requests.get(URL_DADOS, timeout=30, headers={"User-Agent": "GuiaDeSalas/1.0"})
    resposta.raise_for_status()
    dados = resposta.json()
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")

    registros = FonteIcex.interpretar(dados)
    print(f"Salvo em {saida.resolve()}")
    print(f"Registros: {len(registros)}")
    print(f"Disciplinas: {len({r.codigo for r in registros})}")
    print("Prédios:", dict(Counter(r.predio for r in registros)))
    print("Formatos de dia:", sorted({r.dias for r in registros}))

    fonte = FonteIcexArquivo(saida)
    catalogo, relatorio = AtualizadorDeBase([fonte]).atualizar()
    print()
    print(relatorio)
    for registro, motivo in relatorio.recusados[:15]:
        print(f"  recusado: {registro.codigo} {registro.turma} {registro.dias} "
              f"{registro.inicio}-{registro.fim} {registro.sala}: {motivo}")


if __name__ == "__main__":
    main()
