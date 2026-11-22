"""Bot do Telegram: único módulo que depende da biblioteca python-telegram-bot."""

import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from guia_salas.apresentacao.comandos import ComandosDoBot
from guia_salas.apresentacao.formatacao import dividir_mensagem
from guia_salas.dados import FonteDeDados
from guia_salas.dominio import ErroDeDominio
from guia_salas.sistema import Sistema

registro = logging.getLogger(__name__)

TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
COMANDOS = [
    BotCommand("sala", "turmas, horários e salas de uma disciplina"),
    BotCommand("livres", "salas sem aula num dia e hora"),
    BotCommand("minhagrade", "mostra as turmas salvas"),
    BotCommand("adicionar", "salva turmas na grade"),
    BotCommand("remover", "retira uma disciplina da grade"),
    BotCommand("ajuda", "lista de comandos"),
]


class BotGuiaDeSalas:
    """Liga os comandos do Telegram aos ComandosDoBot e agenda a atualização da base."""

    def __init__(self, token: str, sistema: Sistema, fonte: FonteDeDados,
                 intervalo_atualizacao_min: int = 60):
        """Monta a aplicação, registra os tratadores e agenda a primeira atualização para logo após o início."""
        self._sistema = sistema
        self._fonte = fonte
        self._comandos = ComandosDoBot(sistema)
        self._aplicacao = Application.builder().token(token).post_init(self._ao_iniciar).build()
        self._registrar_tratadores()
        if self._aplicacao.job_queue is not None:
            self._aplicacao.job_queue.run_repeating(
                self._atualizar_base, interval=intervalo_atualizacao_min * 60, first=10)

    def executar(self) -> None:
        """Inicia o bot e fica aguardando mensagens."""
        self._aplicacao.run_polling(allowed_updates=Update.ALL_TYPES)

    def _registrar_tratadores(self) -> None:
        """Associa cada comando ao seu tratador."""
        app = self._aplicacao
        app.add_handler(CommandHandler(["start", "ajuda", "help"], self._ajuda))
        app.add_handler(CommandHandler("sala", self._sala))
        app.add_handler(CommandHandler("livres", self._livres))
        app.add_handler(CommandHandler("minhagrade", self._minha_grade))
        app.add_handler(CommandHandler("adicionar", self._adicionar))
        app.add_handler(CommandHandler("remover", self._remover))
        app.add_handler(MessageHandler(filters.Document.MimeType(TIPO_XLSX), self._planilha))
        app.add_handler(MessageHandler(filters.PHOTO, self._planilha_em_imagem))
        app.add_error_handler(self._erro)

    async def _ao_iniciar(self, aplicacao: Application) -> None:
        """Registra a lista de comandos que o Telegram sugere ao digitar /."""
        await aplicacao.bot.set_my_commands(COMANDOS)

    async def _responder(self, update: Update, texto: str) -> None:
        """Envia o texto, dividido em partes que cabem numa mensagem."""
        for parte in dividir_mensagem(texto):
            await update.message.reply_text(parte)

    async def _ajuda(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        await self._responder(update, self._comandos.ajuda())

    async def _sala(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        await self._responder(update, self._comandos.sala(" ".join(contexto.args)))

    async def _livres(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        await self._responder(update, self._comandos.livres(" ".join(contexto.args)))

    async def _minha_grade(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        aluno = ComandosDoBot.aluno_do_chat(update.effective_chat.id)
        texto = await asyncio.to_thread(self._comandos.minha_grade, aluno)
        await self._responder(update, texto)

    async def _adicionar(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        aluno = ComandosDoBot.aluno_do_chat(update.effective_chat.id)
        texto = await asyncio.to_thread(self._comandos.adicionar, aluno, " ".join(contexto.args))
        await self._responder(update, texto)

    async def _remover(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        aluno = ComandosDoBot.aluno_do_chat(update.effective_chat.id)
        texto = await asyncio.to_thread(self._comandos.remover, aluno, " ".join(contexto.args))
        await self._responder(update, texto)

    async def _planilha(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        arquivo = await update.message.document.get_file()
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "grade.xlsx"
            saida = Path(pasta) / "grade_com_salas.xlsx"
            await arquivo.download_to_drive(entrada)
            try:
                legenda = await asyncio.to_thread(self._comandos.planilha, entrada, saida)
            except ErroDeDominio as erro:
                await update.message.reply_text(str(erro))
                return
            with saida.open("rb") as conteudo:
                await update.message.reply_document(document=conteudo, filename="grade_com_salas.xlsx",
                                                    caption=legenda)

    async def _planilha_em_imagem(self, update: Update, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Apenas planilhas .xlsx são aceitas, com as disciplinas na primeira coluna."
        )

    async def _atualizar_base(self, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        """F04 periódica: em caso de recusa, registra o motivo e mantém a base atual."""
        try:
            relatorio = await asyncio.to_thread(self._sistema.atualizacao.atualizar, self._fonte)
        except ErroDeDominio as erro:
            registro.warning("Atualização recusada: %s", erro)
            return
        registro.info("Base atualizada.\n%s", relatorio)

    async def _erro(self, update: object, contexto: ContextTypes.DEFAULT_TYPE) -> None:
        """Registra erros inesperados e avisa o aluno, se houver uma mensagem a responder."""
        registro.error("Erro ao tratar mensagem", exc_info=contexto.error)
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("Não foi possível responder agora. Tente novamente.")
