"""Fontes de dados do quadro de salas do ICEx."""

import json
import re
from abc import abstractmethod
from pathlib import Path

from guia_salas.dados.fonte_base import FonteDeDados, FonteIndisponivel, RegistroDeAula, andar_pelo_numero

PAGINA = "https://www.icex.ufmg.br/icex_novo/minha-salas/"
URL_DADOS = "https://www.icex.ufmg.br/minhasala/recupera_salas.php"
AMOSTRA = Path(__file__).resolve().parent / "amostra_icex.json"
PREDIO_ICEX = "ICEx"
PREDIO_ONLINE = "On-line"


class FonteIcex(FonteDeDados):
    """Fonte abstrata do JSON do quadro de salas do ICEx; subclasses definem de onde ele vem."""

    CAMPOS = {
        "nome": "nome_materia",
        "codigo": "codigo_materia",
        "turma": "turma",
        "inicio": "hora_inicial",
        "fim": "hora_final",
        "dias": "dia_semana",
        "sala": "nome_sala",
    }

    @property
    def nome(self) -> str:
        """Nome da fonte gravado como origem de cada aula."""
        return PREDIO_ICEX

    def coletar(self) -> list[RegistroDeAula]:
        """Obtém o JSON pela forma definida na subclasse e o converte em registros."""
        return self.interpretar(self._obter_json())

    @abstractmethod
    def _obter_json(self) -> dict | list:
        """Devolve o JSON do quadro do ICEx ou lança FonteIndisponivel."""

    @classmethod
    def interpretar(cls, dados: dict | list) -> list[RegistroDeAula]:
        """Converte o JSON do quadro do ICEx em registros."""
        itens = dados.get("records", []) if isinstance(dados, dict) else dados
        if not isinstance(itens, list):
            raise FonteIndisponivel("O JSON não tem a lista de aulas esperada (chave records).")
        registros = []
        for item in itens:
            if not isinstance(item, dict):
                item = {}
            valor = lambda chave: str(item.get(cls.CAMPOS[chave], "") or "").strip()
            predio, sala = separar_predio(valor("sala"))
            registros.append(RegistroDeAula(
                codigo=valor("codigo"),
                nome=valor("nome"),
                turma="".join(valor("turma").split()) or "U",
                dias=valor("dias"),
                inicio=valor("inicio"),
                fim=valor("fim"),
                sala=sala,
                predio=predio,
                andar=andar_pelo_numero(sala) if predio != PREDIO_ONLINE else None,
                origem=PREDIO_ICEX,
            ))
        return registros


class FonteIcexOnline(FonteIcex):
    """Baixa o JSON diretamente do site do ICEx (requer internet e a biblioteca requests)."""

    def __init__(self, url: str = URL_DADOS, sessao=None, tempo_limite: float = 20.0):
        """Guarda o endereço; sessao pode ser qualquer objeto com o método get de requests."""
        self._url = url
        self._sessao = sessao
        self._tempo_limite = tempo_limite

    @property
    def url(self) -> str:
        """Endereço consultado."""
        return self._url

    @property
    def descricao(self) -> str:
        """Endereço do site, gravado no histórico de atualizações."""
        return f"site do ICEx ({self._url})"

    def _obter_json(self) -> dict | list:
        """Faz a requisição HTTP e devolve o JSON."""
        try:
            import requests
        except ImportError as erro:
            raise FonteIndisponivel("Instale a biblioteca requests para baixar os dados.") from erro
        sessao = self._sessao or requests.Session()
        try:
            resposta = sessao.get(self._url, timeout=self._tempo_limite,
                                  headers={"User-Agent": "GuiaDeSalas/1.0"})
            resposta.raise_for_status()
            return resposta.json()
        except (requests.RequestException, ValueError) as erro:
            raise FonteIndisponivel(f"Falha ao consultar o ICEx: {erro}") from erro


class FonteIcexArquivo(FonteIcex):
    """Lê uma cópia local do JSON do ICEx, como a amostra guardada em dados/."""

    def __init__(self, caminho: Path | str = AMOSTRA):
        """Guarda o caminho do arquivo JSON."""
        self._caminho = Path(caminho)

    @property
    def caminho(self) -> Path:
        """Arquivo lido."""
        return self._caminho

    @property
    def descricao(self) -> str:
        """Nome do arquivo, gravado no histórico de atualizações."""
        return f"arquivo {self._caminho.name}"

    def _obter_json(self) -> dict | list:
        """Lê e decodifica o arquivo."""
        try:
            return json.loads(self._caminho.read_text(encoding="utf-8"))
        except (OSError, ValueError) as erro:
            raise FonteIndisponivel(f"Falha ao ler {self._caminho}: {erro}") from erro


def separar_predio(nome_sala: str) -> tuple[str, str]:
    """Separa prédio e sala do nome usado no quadro (ex.: 'CAD3 - Sala 310' -> CAD3, 310)."""
    nome_sala = " ".join(nome_sala.split())
    if nome_sala.upper().replace("-", "") == "ONLINE":
        return PREDIO_ONLINE, nome_sala.upper()
    esquerda, separador, direita = nome_sala.partition(" - ")
    if separador and re.fullmatch(r"(?i)CAD\s*\d+", esquerda):
        sala = re.sub(r"(?i)^sala\s+", "", direita).strip()
        return esquerda.upper().replace(" ", ""), sala
    if separador and direita.strip().upper() == "ICEX":
        return PREDIO_ICEX, esquerda.strip()
    return PREDIO_ICEX, nome_sala
