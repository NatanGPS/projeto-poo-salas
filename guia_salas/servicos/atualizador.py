"""Montagem de um catálogo a partir das fontes de dados."""

from dataclasses import dataclass, field

from guia_salas.dominio import DadoInvalido, DiaSemana, ErroDeDominio, IntervaloDeHorario, Sala
from guia_salas.dados import FonteDeDados, FonteIndisponivel, RegistroDeAula
from guia_salas.servicos.catalogo import CatalogoDeAulas


@dataclass
class RelatorioDeAtualizacao:
    """Resumo de uma atualização: o que entrou, o que foi recusado e o que falhou."""

    registros_lidos: int = 0
    aulas_registradas: int = 0
    recusados: list[tuple[RegistroDeAula, str]] = field(default_factory=list)
    fontes_com_falha: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        linhas = [
            f"Registros lidos: {self.registros_lidos}",
            f"Aulas registradas: {self.aulas_registradas}",
            f"Registros recusados: {len(self.recusados)}",
        ]
        linhas += [f"Fonte com falha: {nome} ({motivo})" for nome, motivo in self.fontes_com_falha.items()]
        return "\n".join(linhas)


class AtualizadorDeBase:
    """Monta um catálogo novo a partir de todas as fontes configuradas."""

    def __init__(self, fontes: list[FonteDeDados]):
        """Recebe as fontes; qualquer subclasse de FonteDeDados serve (polimorfismo em coletar)."""
        self._fontes = fontes

    def atualizar(self) -> tuple[CatalogoDeAulas, RelatorioDeAtualizacao]:
        """Coleta as fontes e devolve o catálogo consolidado com o relatório."""
        catalogo = CatalogoDeAulas()
        relatorio = RelatorioDeAtualizacao()
        for fonte in self._fontes:
            try:
                registros = fonte.coletar()
            except FonteIndisponivel as erro:
                relatorio.fontes_com_falha[fonte.nome] = str(erro)
                continue
            for registro in registros:
                relatorio.registros_lidos += 1
                try:
                    relatorio.aulas_registradas += self.incluir(catalogo, registro)
                except ErroDeDominio as erro:
                    relatorio.recusados.append((registro, str(erro)))
        return catalogo, relatorio

    @staticmethod
    def incluir(catalogo: CatalogoDeAulas, registro: RegistroDeAula) -> int:
        """Converte o registro em aulas do catálogo e devolve quantas foram criadas."""
        dias = DiaSemana.varios_de_texto(registro.dias)
        if not dias:
            raise DadoInvalido(f"Registro sem dia da semana: {registro.codigo} {registro.turma}.")
        intervalo = IntervaloDeHorario.de_texto(registro.inicio, registro.fim)
        sala = Sala.criar(registro.sala, registro.predio, registro.andar)
        antes = len(catalogo)
        for dia in dias:
            catalogo.registrar_aula(registro.codigo, registro.nome, registro.turma,
                                    dia, intervalo, sala, registro.origem)
        return len(catalogo) - antes
