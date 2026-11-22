"""Ponto de entrada: python -m guia_salas [--preparar-base] [--online] [--telegram] [--banco CAMINHO]."""

import argparse
import logging
import sys

from guia_salas.configuracao import Configuracao
from guia_salas.dados import URL_DADOS, FonteIcexOnline
from guia_salas.dominio import ErroDeDominio
from guia_salas.sistema import Sistema, abrir_sistema, preparar_base


def main() -> None:
    """Abre a base e inicia o menu do terminal (padrão) ou o bot do Telegram."""
    configuracao = Configuracao.do_ambiente()
    parser = argparse.ArgumentParser(prog="python -m guia_salas", description="Guia de Salas")
    parser.add_argument("--preparar-base", action="store_true",
                        help="recarregar a base a partir da amostra incluída e encerrar")
    parser.add_argument("--online", action="store_true",
                        help="atualizar a base pelo site do ICEx antes de abrir o menu")
    parser.add_argument("--telegram", action="store_true", help="iniciar o bot do Telegram")
    parser.add_argument("--banco", default=configuracao.caminho_banco,
                        help="arquivo SQLite da base (padrão: base/guia_salas.db)")
    argumentos = parser.parse_args()

    sistema = abrir_sistema(argumentos.banco)
    if argumentos.preparar_base:
        relatorio = preparar_base(sistema)
        print(f"Base preparada em {sistema.banco.caminho}\n{relatorio}")
        return
    if len(sistema.consulta.catalogo) == 0:
        print("Base vazia: carregando a amostra do ICEx incluída no projeto.")
        preparar_base(sistema)

    if argumentos.telegram:
        iniciar_telegram(sistema, configuracao)
        return
    if argumentos.online:
        try:
            print(sistema.atualizacao.atualizar(FonteIcexOnline(URL_DADOS)))
        except ErroDeDominio as erro:
            print(f"Atualização recusada: {erro}")

    from guia_salas.apresentacao.terminal import MenuTerminal
    MenuTerminal(sistema).executar()


def iniciar_telegram(sistema: Sistema, configuracao: Configuracao) -> None:
    """Inicia o bot com o token e a fonte de dados das variáveis de ambiente."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    if not configuracao.token_telegram:
        sys.exit("Defina a variável TELEGRAM_TOKEN para usar o bot.")
    from guia_salas.apresentacao.telegram_bot import BotGuiaDeSalas
    BotGuiaDeSalas(configuracao.token_telegram, sistema, configuracao.criar_fonte(),
                   configuracao.intervalo_atualizacao_min).executar()


if __name__ == "__main__":
    main()
