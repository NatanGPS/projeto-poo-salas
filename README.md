# Guia de Salas

Consulta de salas e horários de aula a partir do quadro "Distribuição de Salas" do ICEx/UFMG (https://www.icex.ufmg.br/icex_novo/minha-salas/).

Trabalho da disciplina Programação Orientada a Objetos (Prof.a Luiza Bernardes Real, 2026/2), de Natan Gaspar de Souza.

## Protótipo (3ª etapa)

O protótipo roda no terminal e demonstra duas funcionalidades:

- **F01: buscar a sala de uma disciplina** pelo nome ou código.
- **F02: consultar salas livres** num dia, hora, andar e prédio.

### Requisitos

- Python 3.10 ou superior (testado com Python 3.13.16).
- Nenhuma biblioteca externa é necessária para o menu e os testes.

### Iniciar o programa

Na pasta do projeto (a que contém este README):

```bash
python -m guia_salas
```

No Linux ou macOS, use `python3` se `python` não existir.

### Executar os testes

```bash
python -m unittest discover -s tests -v
```

### Preparação dos dados

Não há preparação. O programa lê a amostra real incluída em `guia_salas/dados/amostra_icex.json`: 110 registros do quadro do ICEx (disciplinas de MAT, DCC e EST), consultados em 15/10/2026. Os testes usam um subconjunto conhecido em `tests/dados/registros_teste.json`.

Os dados ficam apenas na memória. As consultas não alteram nada, e nada é salvo ao encerrar.

### Opções além do protótipo

Essas opções precisam de bibliotecas externas (`pip install -r requirements.txt`):

| Comando | O que faz |
|---|---|
| `python -m guia_salas --online` | Baixa a lista completa do site do ICEx em vez de usar a amostra (requer internet e `requests`) |
| `python -m guia_salas --telegram` | Inicia o bot do Telegram; precisa da variável `TELEGRAM_TOKEN` (ver `.env.example`) |
| `python scripts/baixar_dados_icex.py` | Salva a lista completa do ICEx em `dados_icex.json` e mostra um resumo |

## Bot no Raspberry Pi

No Raspberry (Raspberry Pi OS), com o projeto baixado:

```bash
git clone https://github.com/NatanGPS/projeto-poo-salas.git
cd projeto-poo-salas
bash deploy/instalar_raspberry.sh
```

O script instala as dependências, pede o token do bot (gravado só em `.env` no Raspberry) e cria o serviço `guia-salas-bot`, que inicia sozinho quando o Raspberry liga.

| Comando | O que faz |
|---|---|
| `sudo systemctl status guia-salas-bot` | mostra se o bot está rodando |
| `journalctl -u guia-salas-bot -f` | mostra o registro do bot |
| `sudo systemctl restart guia-salas-bot` | reinicia o bot |
| `git pull && sudo systemctl restart guia-salas-bot` | atualiza o código e reinicia |

## Estrutura

```
guia_salas/
  __main__.py     ponto de entrada (menu do terminal por padrão)
  terminal.py     MenuTerminal: lê as entradas e executa F01 e F02
  dominio/        Disciplina, Turma, Aula, Sala, DiaSemana, IntervaloDeHorario, erros
  fontes/         FonteDeDados (abstrata) > FonteIcex (abstrata) > FonteIcexOnline, FonteIcexArquivo
  servicos/       CatalogoDeAulas, ConsultaDeSalas, AtualizadorDeBase, PreenchedorDeGrade
  bot/            FormatadorDeRespostas, ComandosDoBot e o bot do Telegram
  dados/          amostra_icex.json
tests/            testes com unittest e dados de teste
scripts/          verificação manual da Aula 17 e download dos dados do ICEx
deploy/           instalação do bot como serviço no Raspberry Pi
exemplos/         planilha de grade para teste
```

## Entregas anteriores

Os PDFs das etapas ficam fora deste ZIP, na pasta `docs/` do projeto:

| Atividade | Arquivo |
|---|---|
| Aulas 13 e 14: modelo de domínio e diagramas de sequência | `docs/aula13-14/Guia-de-Salas-Aulas-13-14.pdf` |
| Aula 17: testes manuais | `docs/aula17/Guia-de-Salas-Testes-Aula-17.pdf` |
| Protótipo | `docs/prototipo/Guia-de-Salas-Prototipo.pdf` |
