"""Leitura das configurações a partir de variáveis de ambiente."""

import os
from dataclasses import dataclass

from guia_salas.dados import AMOSTRA, URL_DADOS, FonteDeDados, FonteIcexArquivo, FonteIcexOnline
from guia_salas.sistema import BANCO_PADRAO


@dataclass(frozen=True)
class Configuracao:
    """Parâmetros de execução: token do bot, origem dos dados, intervalo de atualização e arquivo da base."""

    token_telegram: str = ""
    dados_icex: str = URL_DADOS
    intervalo_atualizacao_min: int = 60
    caminho_banco: str = str(BANCO_PADRAO)

    @classmethod
    def do_ambiente(cls) -> "Configuracao":
        """Monta a configuração a partir de TELEGRAM_TOKEN e das variáveis GUIA_SALAS_*."""
        intervalo = os.getenv("GUIA_SALAS_INTERVALO_MIN", "60")
        try:
            minutos = max(1, int(intervalo))
        except ValueError:
            minutos = 60
        return cls(
            token_telegram=os.getenv("TELEGRAM_TOKEN", ""),
            dados_icex=os.getenv("GUIA_SALAS_DADOS_ICEX", "") or URL_DADOS,
            intervalo_atualizacao_min=minutos,
            caminho_banco=os.getenv("GUIA_SALAS_BANCO", "") or str(BANCO_PADRAO),
        )

    def criar_fonte(self) -> FonteDeDados:
        """Fonte online para endereços http(s); fonte de arquivo para caminhos locais."""
        if self.dados_icex.startswith(("http://", "https://")):
            return FonteIcexOnline(self.dados_icex)
        return FonteIcexArquivo(self.dados_icex or AMOSTRA)
