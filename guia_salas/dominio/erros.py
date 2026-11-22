"""Exceções do domínio."""


class ErroDeDominio(Exception):
    """Base para erros de regra do domínio."""


class DadoInvalido(ErroDeDominio):
    """Valor que não respeita as restrições do domínio."""


class ConflitoDeHorario(ErroDeDominio):
    """Duas aulas ocupando o mesmo lugar ou turma no mesmo horário."""


class TermoDeBuscaInvalido(ErroDeDominio):
    """Termo de busca vazio ou curto demais."""


class PredioDesconhecido(ErroDeDominio):
    """Prédio que não aparece em nenhuma aula da base."""
