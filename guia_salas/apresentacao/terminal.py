"""Menu de texto do Guia de Salas."""

from pathlib import Path
from typing import Callable

from guia_salas.apresentacao.formatacao import FormatadorDeRespostas
from guia_salas.dados import URL_DADOS, FonteDeDados, FonteIcexArquivo, FonteIcexOnline
from guia_salas.dominio import DadoInvalido, DiaSemana, ErroDeDominio, ler_hora
from guia_salas.sistema import Sistema

OPCOES = (
    "1 - Buscar a sala de uma disciplina",
    "2 - Consultar salas livres",
    "3 - Preencher planilha de disciplinas",
    "4 - Minha grade",
    "5 - Atualizar a base de aulas",
    "0 - Sair",
)

OPCOES_DA_GRADE = (
    "1 - Ver a grade",
    "2 - Adicionar turmas",
    "3 - Remover disciplina",
    "4 - Alterar o nome da grade",
    "0 - Voltar",
)


class MenuTerminal:
    """Lê as escolhas do usuário, chama os serviços e mostra as respostas; não contém regras."""

    def __init__(self, sistema: Sistema, ler: Callable[[str], str] = input,
                 escrever: Callable[[str], None] = print,
                 formatador: FormatadorDeRespostas | None = None):
        """Recebe o sistema montado e as funções de leitura e escrita (input e print por padrão)."""
        self._sistema = sistema
        self._ler = ler
        self._escrever = escrever
        self._formatador = formatador or FormatadorDeRespostas()

    def executar(self) -> None:
        """Mostra o menu até o usuário escolher sair ou a entrada terminar."""
        self._escrever("=== Guia de Salas (ICEx) ===")
        self._escrever(self._situacao_da_base())
        acoes = {
            "1": self.buscar_disciplina,
            "2": self.consultar_salas_livres,
            "3": self.preencher_planilha,
            "4": self.minha_grade,
            "5": self.atualizar_base,
        }
        while True:
            self._escrever("\n" + "\n".join(OPCOES))
            try:
                opcao = self._ler("Opção: ").strip()
                if opcao == "0":
                    break
                acao = acoes.get(opcao)
                if acao is None:
                    self._escrever("Opção inválida. Digite um número de 0 a 5.")
                    continue
                acao()
            except EOFError:
                break
        self._escrever("Encerrado.")

    def buscar_disciplina(self) -> None:
        """F01: pede o nome ou código e mostra as turmas, dias, horários e salas."""
        termo = self._ler("Nome ou código da disciplina: ")
        try:
            resultado = self._sistema.consulta.buscar_por_disciplina(termo)
        except ErroDeDominio as erro:
            self._recusar(erro)
            return
        self._escrever(self._formatador.busca(resultado))

    def consultar_salas_livres(self) -> None:
        """F02: pede dia, hora, andar e prédio e mostra as salas sem aula naquele instante."""
        consulta = self._sistema.consulta
        try:
            dia = DiaSemana.de_texto(self._ler("Dia (seg, ter, qua, qui, sex, sab): "))
            instante = ler_hora(self._ler("Hora (HH:MM): "))
            andar = self.ler_andar(self._ler("Andar (vazio para todos): "))
            predio = self._ler(f"Prédio ({', '.join(consulta.catalogo.predios)}, vazio para todos): ").strip()
            salas = consulta.salas_livres(dia, instante, andar, predio or None)
        except ErroDeDominio as erro:
            self._recusar(erro)
            return
        self._escrever(self._formatador.salas_livres(salas, dia, instante, andar))

    def preencher_planilha(self) -> None:
        """F03: pede o caminho da planilha e grava a cópia preenchida ao lado dela."""
        caminho = self._ler("Caminho da planilha .xlsx: ").strip().strip('"')
        try:
            resultado = self._sistema.planilha.preencher(Path(caminho))
        except ErroDeDominio as erro:
            self._recusar(erro)
            return
        self._escrever(self._formatador.planilha(resultado))
        self._escrever(f"Planilha gerada: {resultado.saida}")

    def minha_grade(self) -> None:
        """F05: identifica a grade e mostra o submenu de consulta e alteração."""
        servico = self._sistema.minha_grade
        try:
            grade = servico.abrir(self._ler("Identificação da grade (apelido, ex.: ana): "))
        except ErroDeDominio as erro:
            self._recusar(erro)
            return
        aluno = grade.identificador
        while True:
            self._escrever(f"\n{grade}\n" + "\n".join(OPCOES_DA_GRADE))
            opcao = self._ler("Opção: ").strip()
            try:
                if opcao == "0":
                    return
                if opcao == "1":
                    self._escrever(self._formatador.grade(servico.abrir(aluno)))
                elif opcao == "2":
                    turmas = servico.adicionar(aluno, self._ler("Turmas (ex.: DCC011 TB; MAT001 TA1): "))
                    self._escrever(self._formatador.turmas_adicionadas(turmas))
                elif opcao == "3":
                    codigo = servico.remover(aluno, self._ler("Código da disciplina: "))
                    self._escrever(self._formatador.disciplina_removida(codigo))
                elif opcao == "4":
                    grade = servico.renomear(aluno, self._ler("Novo nome: "))
                    self._escrever(f"Nome alterado para {grade.nome}.")
                else:
                    self._escrever("Opção inválida. Digite um número de 0 a 4.")
                grade = servico.abrir(aluno)
            except ErroDeDominio as erro:
                self._recusar(erro)

    def atualizar_base(self) -> None:
        """F04: escolhe a origem dos dados e substitui a base se a carga for aceita."""
        escolha = self._ler("Origem (1 - site do ICEx, 2 - arquivo JSON): ").strip()
        fonte: FonteDeDados
        if escolha == "1":
            fonte = FonteIcexOnline(URL_DADOS)
        elif escolha == "2":
            fonte = FonteIcexArquivo(self._ler("Caminho do arquivo JSON: ").strip().strip('"'))
        else:
            self._escrever("Origem inválida. Digite 1 ou 2.")
            return
        self._escrever("Atualizando...")
        try:
            relatorio = self._sistema.atualizacao.atualizar(fonte)
        except ErroDeDominio as erro:
            self._recusar(erro)
            return
        self._escrever(self._formatador.atualizacao(relatorio))
        self._escrever(self._situacao_da_base())

    @staticmethod
    def ler_andar(texto: str) -> int | None:
        """Converte o andar digitado; vazio significa todos os andares."""
        texto = texto.strip()
        if not texto:
            return None
        try:
            return int(texto)
        except ValueError as erro:
            raise DadoInvalido(f"Andar inválido: \"{texto}\". Use um número, como 2.") from erro

    def _situacao_da_base(self) -> str:
        """Tamanho da base e data da última atualização."""
        catalogo = self._sistema.consulta.catalogo
        return self._formatador.situacao_da_base(
            len(catalogo.disciplinas), len(catalogo), self._sistema.repositorio_aulas.ultima_atualizacao())

    def _recusar(self, erro: ErroDeDominio) -> None:
        """Mostra o motivo de uma recusa; nada foi alterado."""
        self._escrever(f"Entrada recusada: {erro}")
