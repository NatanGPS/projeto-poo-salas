"""F04: atualização da base de aulas a partir de uma fonte externa."""

from guia_salas.dados import FalhaNaBase, FonteDeDados, RegistroDeAtualizacao, RepositorioDeAulas
from guia_salas.dominio import AtualizacaoRecusada
from guia_salas.servicos.atualizador import AtualizadorDeBase, RelatorioDeAtualizacao
from guia_salas.servicos.consulta import ConsultaDeSalas

PROPORCAO_MINIMA_ACEITA = 0.5


class ServicoDeAtualizacao:
    """Valida uma carga nova, grava na base e só então troca o catálogo das consultas."""

    def __init__(self, consulta: ConsultaDeSalas, repositorio: RepositorioDeAulas):
        """Recebe a consulta cujo catálogo será trocado e o repositório que grava as aulas."""
        self._consulta = consulta
        self._repositorio = repositorio

    def atualizar(self, fonte: FonteDeDados) -> RelatorioDeAtualizacao:
        """Substitui a base pela carga da fonte; recusa falha, carga vazia ou mais da metade recusada."""
        catalogo, relatorio = AtualizadorDeBase([fonte]).atualizar()
        if relatorio.fontes_com_falha:
            motivo = "; ".join(relatorio.fontes_com_falha.values())
            raise AtualizacaoRecusada(f"Fonte indisponível: {motivo}. A base anterior foi mantida.")
        if len(catalogo) == 0:
            raise AtualizacaoRecusada("A fonte não trouxe nenhuma aula válida. A base anterior foi mantida.")
        aceitos = relatorio.registros_lidos - len(relatorio.recusados)
        if aceitos < relatorio.registros_lidos * PROPORCAO_MINIMA_ACEITA:
            raise AtualizacaoRecusada(
                f"{len(relatorio.recusados)} de {relatorio.registros_lidos} registros foram recusados; "
                "o formato da fonte pode ter mudado. A base anterior foi mantida."
            )
        try:
            self._repositorio.substituir(catalogo, RegistroDeAtualizacao(
                momento=self._repositorio.agora(),
                origem=fonte.descricao,
                registros_lidos=relatorio.registros_lidos,
                aulas_registradas=relatorio.aulas_registradas,
                registros_recusados=len(relatorio.recusados),
            ))
        except FalhaNaBase as erro:
            raise AtualizacaoRecusada(f"Falha ao gravar a base: {erro}. A base anterior foi mantida.") from erro
        self._consulta.trocar_catalogo(catalogo)
        return relatorio
