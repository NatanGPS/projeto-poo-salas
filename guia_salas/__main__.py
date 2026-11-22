"""Ponto de entrada: python -m guia_salas [--online] [--telegram]."""

import argparse
import logging
import sys

from guia_salas.configuracao import Configuracao
from guia_salas.fontes import AMOSTRA, URL_DADOS, FonteIcexArquivo, FonteIcexOnline
from guia_salas.servicos.atualizador import AtualizadorDeBase
from guia_salas.servicos.consulta import ConsultaDeSalas
from guia_salas.terminal import MenuTerminal


def main() -> None:
    """Carrega a base e abre o menu do terminal (padrão) ou o bot do Telegram."""
    parser = argparse.ArgumentParser(description="Guia de Salas")
    parser.add_argument("--online", action="store_true",
                        help="baixar a lista completa do site do ICEx em vez de usar a amostra local")
    parser.add_argument("--telegram", action="store_true", help="iniciar o bot do Telegram")
    argumentos = parser.parse_args()

    if argumentos.telegram:
        iniciar_telegram()
        return

    fonte = FonteIcexOnline(URL_DADOS) if argumentos.online else FonteIcexArquivo(AMOSTRA)
    catalogo, relatorio = AtualizadorDeBase([fonte]).atualizar()
    if len(catalogo) == 0:
        sys.exit(f"Não foi possível carregar a base.\n{relatorio}")
    origem = "lista completa do site do ICEx" if argumentos.online else "amostra real do ICEx (15/10/2026)"
    descricao = (f"Base: {origem}, {len(catalogo.disciplinas)} disciplinas, "
                 f"{len(catalogo)} aulas, {len(relatorio.recusados)} registros recusados.")
    MenuTerminal(ConsultaDeSalas(catalogo), descricao).executar()


def iniciar_telegram() -> None:
    """Inicia o bot com a configuração das variáveis de ambiente."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    configuracao = Configuracao.do_ambiente()
    if not configuracao.token_telegram:
        sys.exit("Defina a variável TELEGRAM_TOKEN para usar o bot.")
    atualizador = AtualizadorDeBase(configuracao.criar_fontes())
    catalogo, relatorio = atualizador.atualizar()
    logging.info("Base carregada.\n%s", relatorio)
    from guia_salas.bot.aplicacao import BotGuiaDeSalas
    BotGuiaDeSalas(configuracao.token_telegram, ConsultaDeSalas(catalogo), atualizador,
                   configuracao.intervalo_atualizacao_min).executar()


if __name__ == "__main__":
    main()
