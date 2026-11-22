"""Montagem da aplicação do Telegram."""

import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from guia_salas.bot.comandos import ComandosDoBot
from guia_salas.bot.formatacao import dividir_mensagem
from guia_salas.dominio import DadoInvalido
from guia_salas.servicos.atualizador import AtualizadorDeBase
from guia_salas.servicos.consulta import ConsultaDeSalas
from guia_salas.servicos.grade import PreenchedorDeGrade

registro = logging.getLogger(__name__)

TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class BotGuiaDeSalas:
    """Liga os comandos do Telegram às consultas do Guia de Salas."""

    def __init__(self, token: str, consulta: ConsultaDeSalas, atualizador: AtualizadorDeBase,
                 intervalo_atualizacao_min: int = 60):
        self._consulta = consulta
        self._comandos = ComandosDoBot(consulta)
        self._preenchedor = PreenchedorDeGrade(consulta)
        self._atualizador = atualizador
        self._aplicacao = Application.builder().token(token).build()
        self._registrar_tratadores()
        if self._aplicacao.job_queue is not None:
            self._aplicacao.job_queue.run_repeating(
                self._atualizar_base, interval=intervalo_atualizacao_min * 60, first=intervalo_atualizacao_min * 60
            )

    def executar(self) -> None:
        """Inicia o bot e fica aguardando mensagens."""
        self._aplicacao.run_polling(allowed_updates=Update.ALL_TYPES)

    def _registrar_tratadores(self) -> None:
        """Associa cada comando ao seu tratador."""
        app = self._aplicacao
        app.add_handler(CommandHandler(["start", "ajuda", "help"], self._ajuda))
        app.add_handler(CommandHandler("sala", self._sala))
        app.add_handler(CommandHandler("livres", self._livres))
        app.add_handler(MessageHandler(filters.Document.MimeType(TIPO_XLSX), self._grade))
        app.add_handler(MessageHandler(filters.PHOTO, self._grade_em_imagem))

    async def _ajuda(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(self._comandos.ajuda())

    async def _sala(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        for parte in dividir_mensagem(self._comandos.sala(" ".join(contexto.args))):
            await update.message.reply_text(parte)

    async def _livres(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        for parte in dividir_mensagem(self._comandos.livres(" ".join(contexto.args))):
            await update.message.reply_text(parte)

    async def _grade(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        arquivo = await update.message.document.get_file()
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "grade.xlsx"
            saida = Path(pasta) / "grade_com_salas.xlsx"
            await arquivo.download_to_drive(entrada)
            localizadas, nao_localizadas = self._preenchedor.preencher(entrada, saida)
            await update.message.reply_document(
                document=saida.open("rb"),
                filename="grade_com_salas.xlsx",
                caption=f"{localizadas} disciplina(s) localizada(s), {nao_localizadas} não localizada(s).",
            )

    async def _grade_em_imagem(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Apenas planilhas .xlsx são aceitas, com as disciplinas na primeira coluna."
        )

    async def _atualizar_base(self, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        catalogo, relatorio = self._atualizador.atualizar()
        try:
            self._consulta.trocar_catalogo(catalogo)
        except DadoInvalido as erro:
            registro.warning("%s\n%s", erro, relatorio)
            return
        registro.info("Base atualizada.\n%s", relatorio)
