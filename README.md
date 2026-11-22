# Guia de Salas

Consulta de salas e horários de aula a partir do quadro "Distribuição de Salas" do ICEx/UFMG (https://www.icex.ufmg.br/icex_novo/minha-salas/), pelo terminal ou por um bot do Telegram.

Trabalho da disciplina Programação Orientada a Objetos (Prof.a Luiza Bernardes Real, 2026/2), de Natan Gaspar de Souza. Versão 1.0.0 (produto final, 4ª etapa).

## Funcionalidades

| ID | Funcionalidade | Terminal | Telegram |
|---|---|---|---|
| F01 | Buscar a sala de uma disciplina pelo nome ou código | opção 1 | `/sala banco de dados` |
| F02 | Consultar salas livres num dia, hora, andar e prédio | opção 2 | `/livres ter 14:00 1` |
| F03 | Preencher uma planilha .xlsx de disciplinas com turma, horários e sala | opção 3 | enviar o arquivo .xlsx |
| F04 | Atualizar a base de aulas pelo site do ICEx ou por um arquivo JSON | opção 5 | automática a cada 60 min |
| F05 | Minha grade: salvar turmas, ver a semana, remover e renomear | opção 4 | `/minhagrade`, `/adicionar`, `/remover` |

## Requisitos

- Python 3.10 ou superior (testado com Python 3.13.18).
- Dependências: `pip install -r requirements.txt`
  - `openpyxl` (F03 e testes da F03)
  - `requests` (F04 pelo site do ICEx)
  - `python-telegram-bot[job-queue]` (somente para o bot)
- F01, F02, F04 por arquivo e F05 funcionam só com a biblioteca padrão.

Recomenda-se um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Base de dados

A base é um arquivo SQLite em `base/guia_salas.db`. O ZIP da entrega já traz a base preenchida. Para criá-la de novo a partir da amostra incluída:

```bash
python -m guia_salas --preparar-base
```

O comando grava as 110 aulas reais da amostra do ICEx (`guia_salas/dados/amostra_icex.json`, consultada em 15/10/2026: 30 disciplinas, 199 aulas, 42 salas presenciais) e uma grade fictícia de exemplo com o identificador `ana`. As grades já gravadas são mantidas. Se o arquivo da base não existir, o programa cria e preenche a base sozinho na primeira execução.

Outro arquivo pode ser usado com `--banco caminho/arquivo.db` ou com a variável `GUIA_SALAS_BANCO`.

## Iniciar o sistema

Na pasta do projeto (a que contém este README):

```bash
python -m guia_salas                 # menu do terminal
python -m guia_salas --online        # atualiza pelo site do ICEx antes de abrir o menu
python -m guia_salas --telegram      # bot do Telegram (precisa de TELEGRAM_TOKEN)
```

No Linux ou macOS, use `python3` se `python` não existir.

Exemplo de uso no terminal: opção 4, identificação `ana`, opção 1 mostra a grade de exemplo. A planilha `exemplos/grade_exemplo.xlsx` serve para testar a opção 3; a cópia preenchida é gravada ao lado, como `grade_exemplo_com_salas.xlsx`.

## Executar os testes

```bash
python -m unittest discover -s tests -v
```

Os testes criam uma base SQLite nova numa pasta temporária para cada caso e nunca usam `base/guia_salas.db`. Os dados de teste ficam em `tests/dados/`.

## Bot no Raspberry Pi

```bash
git clone https://github.com/NatanGPS/projeto-poo-salas.git
cd projeto-poo-salas
bash deploy/instalar_raspberry.sh
```

O script instala as dependências, pede o token do bot (gravado só em `.env`) e cria o serviço `guia-salas-bot`. Para atualizar o código: `git pull && sudo systemctl restart guia-salas-bot`. A base do bot fica em `base/guia_salas.db` no Raspberry e é atualizada pelo site do ICEx logo após o início e depois a cada `GUIA_SALAS_INTERVALO_MIN` minutos.

## Estrutura

```
guia_salas/
  __main__.py       ponto de entrada (menu do terminal por padrão)
  sistema.py        monta a base, os repositórios e os serviços
  configuracao.py   variáveis de ambiente
  apresentacao/     MenuTerminal, ComandosDoBot, BotGuiaDeSalas, FormatadorDeRespostas
  servicos/         ConsultaDeSalas, CatalogoDeAulas, PreenchedorDeGrade, ServicoDeAtualizacao,
                    AtualizadorDeBase, ServicoMinhaGrade
  dominio/          Disciplina, Turma, Aula, Sala, SalaOnline, GradeDoAluno, DiaSemana,
                    IntervaloDeHorario, exceções
  dados/            FonteDeDados (abstrata), FonteIcex, FonteIcexOnline, FonteIcexArquivo,
                    FonteBancoLocal, BancoDeDados, repositórios e amostra_icex.json
base/               guia_salas.db (gerado; fora do Git)
tests/              testes unittest e dados de teste
exemplos/           planilha de exemplo para a F03
scripts/            download da lista completa do ICEx
deploy/             instalação do bot como serviço no Raspberry Pi
```

## Documentos

Os PDFs das etapas ficam na pasta `docs/` do repositório (fora do ZIP de código):

| Etapa | Arquivo |
|---|---|
| Aulas 13 e 14: modelo de domínio e diagramas de sequência | `docs/aula13-14/Guia-de-Salas-Aulas-13-14.pdf` |
| Aula 17: testes manuais | `docs/aula17/Guia-de-Salas-Testes-Aula-17.pdf` |
| Protótipo | `docs/prototipo/Guia-de-Salas-Prototipo.pdf` |
| Produto final | `docs/produto-final/Guia-de-Salas-Produto-Final.pdf` |
