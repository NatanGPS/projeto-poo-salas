"""Exceções do domínio e das regras de negócio."""


class ErroDeDominio(Exception):
    """Base de toda recusa por regra; a interface mostra a mensagem ao usuário."""


class DadoInvalido(ErroDeDominio):
    """Valor que não respeita o formato ou as restrições esperadas."""


class ConflitoDeHorario(ErroDeDominio):
    """Duas aulas da mesma turma ou da mesma grade no mesmo horário."""


class TermoDeBuscaInvalido(ErroDeDominio):
    """Termo de busca vazio ou curto demais."""


class PredioDesconhecido(ErroDeDominio):
    """Prédio que não aparece em nenhuma aula da base."""


class NaoEncontrado(ErroDeDominio):
    """Disciplina ou turma inexistente na base, ou disciplina ausente da grade."""


class Duplicidade(ErroDeDominio):
    """Disciplina repetida no pedido ou já presente na grade."""


class LimiteExcedido(ErroDeDominio):
    """Operação que ultrapassaria um limite definido pelas regras."""


class PlanilhaInvalida(ErroDeDominio):
    """Planilha inexistente, em formato errado ou sem disciplinas."""


class AtualizacaoRecusada(ErroDeDominio):
    """Atualização da base recusada; a base anterior é mantida."""


class GravacaoFalhou(ErroDeDominio):
    """A base de dados falhou ao ler ou gravar; nada foi alterado."""
