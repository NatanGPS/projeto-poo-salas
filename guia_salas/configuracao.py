"""Leitura das configurações a partir de variáveis de ambiente."""

import os
from dataclasses import dataclass

from guia_salas.fontes import AMOSTRA, URL_DADOS, FonteDeDados, FonteIcexArquivo, FonteIcexOnline


@dataclass(frozen=True)
class Configuracao:
    """Parâmetros de execução: token do bot, origem dos dados e intervalo de atualização."""

    token_telegram: str = ""
    dados_icex: str = URL_DADOS
    intervalo_atualizacao_min: int = 60

    @classmethod
    def do_ambiente(cls) -> "Configuracao":
        """Monta a configuração a partir de TELEGRAM_TOKEN e das variáveis GUIA_SALAS_*."""
        return cls(
            token_telegram=os.getenv("TELEGRAM_TOKEN", ""),
            dados_icex=os.getenv("GUIA_SALAS_DADOS_ICEX", "") or URL_DADOS,
            intervalo_atualizacao_min=int(os.getenv("GUIA_SALAS_INTERVALO_MIN", "60")),
        )

    def criar_fontes(self) -> list[FonteDeDados]:
        """Fonte online para endereços http(s); fonte de arquivo para caminhos locais."""
        if self.dados_icex.startswith(("http://", "https://")):
            return [FonteIcexOnline(self.dados_icex)]
        return [FonteIcexArquivo(self.dados_icex or AMOSTRA)]
