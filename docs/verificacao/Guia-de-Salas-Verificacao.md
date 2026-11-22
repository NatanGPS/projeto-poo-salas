# Guia de Salas: Verificação do produto final (5ª etapa)

Natan Gaspar de Souza

**Versão verificada:** 1.0.0, a mesma do produto final: arquivo `guia-salas-1.0.0.zip` (SHA-256 `7e06d28c73761ade0cdc62561dcd7104d900cbacec215b65bfa205e53f7f0e56`), commit `41aee24`. Os testes foram executados no conteúdo extraído desse ZIP em 22/11/2026, com Python 3.13.18.

**Resultado da última execução:** 85 testes `unittest`, 85 aprovados, nenhuma falha. São 59 cenários ligados às funcionalidades F01 a F05 e 8 verificações complementares de domínio, fontes e menu (seção 7).

## 1. Como reproduzir

| Item | Onde está |
|---|---|
| Testes | Pasta `tests/` do ZIP: `test_f01_busca.py` a `test_f05_minha_grade.py`, `test_dominio.py`, `test_fontes.py`, `test_menu.py`; apoio em `tests/apoio.py` |
| Dados de teste | `tests/dados/registros_teste.json` (11 registros reais do ICEx: 7 disciplinas, 19 aulas), `tests/dados/registros_grade_cheia.json` (9 disciplinas fictícias sem conflito), `exemplos/grade_exemplo.xlsx`, `guia_salas/dados/amostra_icex.json` |
| Comando | Na pasta do projeto: `pip install -r requirements.txt` e depois `python -m unittest discover -s tests -v` |
| Evidência | Saída completa da execução no Anexo A, com as linhas numeradas |

**Base de teste separada.** A classe `TesteComBase` (`tests/apoio.py`) cria, antes de cada teste, uma pasta temporária com um arquivo SQLite novo (`teste.db`), carregado a partir de `tests/dados/`, e apaga a pasta ao final. A base de demonstração `base/guia_salas.db` nunca é aberta pelos testes. Como cada teste prepara o próprio estado, o resultado não depende da ordem de execução.

**Como o estado é comparado.** Nas consultas e recusas, os testes tiram um retrato antes e depois da operação: `retrato(catalogo)` lista todas as aulas do catálogo em memória e `retrato_banco(banco)` lista todas as linhas das sete tabelas do SQLite. "Catálogo igual" e "base igual" nas tabelas abaixo significam que esses retratos ficaram idênticos.

## 2. F01. Buscar a sala de uma disciplina

**Regras verificadas.** Termo com pelo menos 3 caracteres; corresponde pelo código exato (sem diferenciar maiúsculas) ou por palavras do nome, ignorando acentos, com algarismos 1 a 9 equivalentes a romanos; resultado vazio é válido; a consulta não altera dados.

**Preparação e estado inicial.** C01 a C07: catálogo em memória montado de `registros_teste.json` (7 disciplinas, 19 aulas). C08 a C10: base de teste SQLite com os mesmos registros, usada pelos comandos do bot.

| ID | Regra e entrada | Resultado e estado final esperados | Resultado e estado final observados | Situação | Evidência |
|---|---|---|---|---|---|
| F01-C01 | Busca por nome. "banco de dados". | Devolve DCC011 com TB (seg e qua, 09:25-11:05, sala 2014 - DCC, ICEx) e TE (ter e qui, 19:00-20:40, sala 213, CAD3). Catálogo igual ao inicial. | DCC011 com as 4 aulas esperadas, na ordem esperada. Retrato do catálogo igual ao inicial. | Aprovado | `test_f01_busca.py`<br>`test_c01_busca_por_nome_devolve_turmas_e_salas`<br>Anexo A, linha 16 |
| F01-C02 | Busca por código com minúsculas e espaços. "  dcc024 ". | Devolve somente DCC024. Catálogo igual. | Somente DCC024. Catálogo igual. | Aprovado | `test_f01_busca.py`<br>`test_c02_busca_por_codigo_ignora_maiusculas_e_espacos`<br>Anexo A, linha 17 |
| F01-C03 | Acento e algarismo. "Cálculo 1". | Devolve MAT001 (CALCULO DIFERENCIAL E INTEGRAL I). | Somente MAT001. | Aprovado | `test_f01_busca.py`<br>`test_c03_algarismo_equivale_a_romano_e_acentos_sao_ignorados`<br>Anexo A, linha 18 |
| F01-C04 | Limite mínimo do termo. "ban" (3 caracteres). | Aceita e devolve DCC011. | Aceito; devolve DCC011. | Aprovado | `test_f01_busca.py`<br>`test_c04_termo_com_tres_caracteres_e_aceito`<br>Anexo A, linha 19 |
| F01-C05 | Abaixo do mínimo. "  C " e "ba". | Rejeita com TermoDeBuscaInvalido. Catálogo igual. | TermoDeBuscaInvalido nos dois casos. Catálogo igual. | Aprovado | `test_f01_busca.py`<br>`test_c05_termo_curto_e_rejeitado_sem_alterar_catalogo`<br>Anexo A, linha 20 |
| F01-C06 | Disciplina fora do quadro. "Programação Orientada a Objetos". | Resultado vazio válido (encontrou = falso), sem erro. Catálogo igual. | Resultado vazio, sem exceção. Catálogo igual. | Aprovado | `test_f01_busca.py`<br>`test_c06_disciplina_ausente_devolve_resultado_vazio_valido`<br>Anexo A, linha 21 |
| F01-C07 | Termo comum a várias disciplinas. "computadores". | Devolve DCC001, DCC006 e DCC017, em ordem de código. | DCC001, DCC006 e DCC017. | Aprovado | `test_f01_busca.py`<br>`test_c07_termo_comum_a_varias_disciplinas_devolve_todas`<br>Anexo A, linha 22 |
| F01-C08 | Comando do bot. /sala DCC011. | Texto com "DCC011 - INTRODUCAO A BANCO DE DADOS" e a linha da turma TE. Base SQLite igual. | Texto com as duas linhas esperadas. Todas as tabelas da base iguais. | Aprovado | `test_f01_busca.py`<br>`test_c08_comando_sala_responde_e_nao_altera_a_base`<br>Anexo A, linha 23 |
| F01-C09 | Comando do bot com termo curto. /sala C. | Mensagem "Informe ao menos 3 caracteres..." com o exemplo de uso. | Mensagem e exemplo presentes. | Aprovado | `test_f01_busca.py`<br>`test_c09_comando_sala_com_termo_curto_mostra_exemplo`<br>Anexo A, linha 24 |
| F01-C10 | Resposta longa. Texto de 1000 linhas, limite 4000 caracteres. | Partes com no máximo 4000 caracteres que, juntas, reproduzem o texto. | Todas as partes dentro do limite; texto reconstruído igual. | Aprovado | `test_f01_busca.py`<br>`test_c10_resposta_longa_e_dividida_entre_linhas`<br>Anexo A, linha 25 |

## 3. F02. Consultar salas livres

**Regras verificadas.** Sala ocupada quando uma aula a usa no dia com início ≤ hora < fim; turmas conjuntas ocupam a sala; sala on-line nunca é livre; dia, hora, andar e prédio validados; lista vazia é válida; a consulta não altera dados.

**Preparação e estado inicial.** C01 a C09: catálogo em memória de `registros_teste.json`. No 2º andar do ICEx há 2009 - DCC, 2013 - DCC e 2014 - DCC; a 2014 - DCC tem DCC011 TB na segunda, 09:25-11:05; a sala 407 do CAD3 tem DCC006 TL1 e DCC017 TN na segunda, 14:55-16:35; MAT001 TOL1 é on-line. C10 a C12: base de teste SQLite com os mesmos registros.

| ID | Regra e entrada | Resultado e estado final esperados | Resultado e estado final observados | Situação | Evidência |
|---|---|---|---|---|---|
| F02-C01 | Sala ocupada. Seg, 09:30, andar 2, "icex". | Devolve 2009 - DCC e 2013 - DCC; 2014 - DCC (DCC011 TB) não aparece. Catálogo igual. | [2009 - DCC, 2013 - DCC]. Catálogo igual. | Aprovado | `test_f02_salas_livres.py`<br>`test_c01_sala_ocupada_nao_aparece`<br>Anexo A, linha 29 |
| F02-C02 | Limite: horário de término. Seg, 11:05, andar 2, ICEx. | 2014 - DCC aparece livre (fim exclusivo). | 2014 - DCC na lista. | Aprovado | `test_f02_salas_livres.py`<br>`test_c02_sala_fica_livre_no_horario_de_termino`<br>Anexo A, linha 30 |
| F02-C03 | Limite: horário de início. Seg, 09:25, andar 2, ICEx. | 2014 - DCC não aparece (início inclusivo). | 2014 - DCC fora da lista. | Aprovado | `test_f02_salas_livres.py`<br>`test_c03_sala_ocupada_no_horario_de_inicio`<br>Anexo A, linha 31 |
| F02-C04 | Turma conjunta. Seg, 15:00, todos os andares, CAD3. | Sala 407 ocupada; as turmas na sala são DCC006 e DCC017. | 407 fora da lista; ocupantes DCC006 e DCC017. | Aprovado | `test_f02_salas_livres.py`<br>`test_c04_turma_conjunta_ocupa_a_sala`<br>Anexo A, linha 32 |
| F02-C05 | Sala on-line. Sex, 18:00, sem filtros. | ON-LINE nunca aparece como livre. | ON-LINE fora da lista. | Aprovado | `test_f02_salas_livres.py`<br>`test_c05_aula_online_nunca_vira_sala_livre`<br>Anexo A, linha 33 |
| F02-C06 | Prédio inexistente. Ter, 14:00, andar 1, "CAD9". | Rejeita com PredioDesconhecido. Catálogo igual. | PredioDesconhecido. Catálogo igual. | Aprovado | `test_f02_salas_livres.py`<br>`test_c06_predio_desconhecido_e_rejeitado_sem_alterar_catalogo`<br>Anexo A, linha 34 |
| F02-C07 | Andar negativo. Ter, 14:00, andar -1. | Rejeita com DadoInvalido. Catálogo igual. | DadoInvalido. Catálogo igual. | Aprovado | `test_f02_salas_livres.py`<br>`test_c07_andar_negativo_e_rejeitado`<br>Anexo A, linha 35 |
| F02-C08 | Falha de conversão. Horas "25:00", "14", "dez horas", "-1:00"; dia "domingo". | Cada valor é rejeitado com DadoInvalido. | DadoInvalido em todos os casos. | Aprovado | `test_f02_salas_livres.py`<br>`test_c08_hora_e_dia_invalidos_sao_rejeitados_na_conversao`<br>Anexo A, linha 36 |
| F02-C09 | Andar sem salas. Seg, 09:30, andar 9. | Lista vazia válida, sem erro. | Lista vazia. | Aprovado | `test_f02_salas_livres.py`<br>`test_c09_andar_sem_salas_devolve_lista_vazia_valida`<br>Anexo A, linha 37 |
| F02-C10 | Bot sem andar. /livres seg 09:30 icex. | Considera todos os andares do ICEx: inclui 1012, não inclui 2014 - DCC. Base igual. | Cabeçalho "Salas livres (Segunda, 09:30)", 1012 presente, 2014 - DCC ausente. Base igual. | Aprovado | `test_f02_salas_livres.py`<br>`test_c10_livres_sem_andar_considera_todos_e_aceita_predio`<br>Anexo A, linha 26 |
| F02-C11 | Bot com hora inválida. /livres ter 25:00 1. | Mostra "Horário inválido: '25:00'" e o uso do comando. | Motivo e uso presentes. | Aprovado | `test_f02_salas_livres.py`<br>`test_c11_livres_com_hora_invalida_mostra_motivo_e_uso`<br>Anexo A, linha 27 |
| F02-C12 | Bot sem a hora. /livres ter. | Mostra o uso do comando. | Resposta começa com "Uso: /livres". | Aprovado | `test_f02_salas_livres.py`<br>`test_c12_livres_sem_hora_mostra_uso`<br>Anexo A, linha 28 |

## 4. F03. Preencher planilha de disciplinas

**Regras verificadas.** Só aceita arquivo .xlsx existente e legível, com ao menos uma disciplina; cada linha segue a busca da F01 e a coluna "Turma", se houver; linhas não encontradas viram "não localizada" sem interromper as outras; a original nunca é alterada; nenhuma cópia é criada em caso de recusa.

**Preparação e estado inicial.** Base de teste com `registros_teste.json` e uma cópia de `exemplos/grade_exemplo.xlsx` na pasta temporária, cujo hash SHA-256 é guardado antes do teste. Nos cenários C02 e C06 a planilha é criada pelo próprio teste com as linhas indicadas; em C04 e C05 o arquivo é um texto comum.

| ID | Regra e entrada | Resultado e estado final esperados | Resultado e estado final observados | Situação | Evidência |
|---|---|---|---|---|---|
| F03-C01 | Planilha de exemplo (DCC011 TB; Linguagens de Programação; MAT038 TM4; Programação Orientada a Objetos). | 3 localizadas e 1 não localizada; cópia grade_com_salas.xlsx com as 3 colunas novas e valores corretos; original e base iguais. | (3, 1); colunas e linhas conferidas célula a célula; hash da original igual; base igual. | Aprovado | `test_f03_planilha.py`<br>`test_c01_planilha_de_exemplo_e_preenchida`<br>Anexo A, linha 38 |
| F03-C02 | Turma inexistente. DCC011 TZ e DCC024 sem turma. | DCC011 TZ não localizada; DCC024 localizada. | (1, 1). | Aprovado | `test_f03_planilha.py`<br>`test_c02_turma_pedida_inexistente_vira_nao_localizada`<br>Anexo A, linha 39 |
| F03-C03 | Arquivo inexistente. nao_existe.xlsx. | Rejeita com PlanilhaInvalida; nenhuma cópia criada. | PlanilhaInvalida; nao_existe_com_salas.xlsx não existe. | Aprovado | `test_f03_planilha.py`<br>`test_c03_arquivo_inexistente_e_recusado`<br>Anexo A, linha 40 |
| F03-C04 | Extensão errada. grade.csv. | Rejeita com PlanilhaInvalida. | PlanilhaInvalida. | Aprovado | `test_f03_planilha.py`<br>`test_c04_extensao_diferente_de_xlsx_e_recusada`<br>Anexo A, linha 41 |
| F03-C05 | Falha de conversão. falsa.xlsx com texto comum. | Rejeita com PlanilhaInvalida; nenhuma cópia criada. | PlanilhaInvalida; cópia não criada. | Aprovado | `test_f03_planilha.py`<br>`test_c05_arquivo_corrompido_e_recusado`<br>Anexo A, linha 42 |
| F03-C06 | Planilha só com cabeçalho. | Rejeita com PlanilhaInvalida; nenhuma cópia criada. | PlanilhaInvalida; cópia não criada. | Aprovado | `test_f03_planilha.py`<br>`test_c06_planilha_sem_disciplinas_e_recusada`<br>Anexo A, linha 43 |
| F03-C07 | Saída igual à entrada. | Rejeita com PlanilhaInvalida; original intacta. | PlanilhaInvalida; hash da original igual. | Aprovado | `test_f03_planilha.py`<br>`test_c07_saida_igual_a_entrada_e_recusada_e_original_preservado`<br>Anexo A, linha 44 |
| F03-C08 | Planilha enviada ao bot (planilha de exemplo). | Legenda "3 disciplina(s) localizada(s), 1 não localizada(s)." e arquivo de resposta criado. | Legenda igual; arquivo criado. | Aprovado | `test_f03_planilha.py`<br>`test_c08_comando_do_bot_devolve_legenda`<br>Anexo A, linha 45 |

## 5. F04. Atualizar a base de aulas

**Regras verificadas.** Recusa a carga se a fonte falhar, se não houver aula válida ou se mais da metade dos registros for recusada (exatamente metade é aceita); grava tudo numa transação; só troca o catálogo depois de gravar; mantém as grades.

**Preparação e estado inicial.** Base de teste carregada de `registros_teste.json`: 7 disciplinas, 19 aulas e 1 linha no histórico. As cargas dos cenários C04 a C07 e C09 são arquivos JSON gravados pelo próprio teste na pasta temporária. Em C03, a fonte online recebe uma sessão HTTP falsa que simula o site fora do ar. Em C08, um gatilho (trigger) criado no SQLite de teste força erro na última inserção. Em C09, a grade "ana" é criada no início do teste.

| ID | Regra e entrada | Resultado e estado final esperados | Resultado e estado final observados | Situação | Evidência |
|---|---|---|---|---|---|
| F04-C01 | Carga válida. Arquivo amostra_icex.json (110 registros). | Aceita: 110 lidos, 199 aulas, 0 recusados; 30 disciplinas; após reabrir, 199 aulas e histórico com 2 cargas. | (110, 199, 0); 30 disciplinas; base reaberta com 199 aulas; histórico [registros_teste.json, amostra_icex.json]. | Aprovado | `test_f04_atualizacao.py`<br>`test_c01_carga_valida_substitui_a_base_e_registra_historico`<br>Anexo A, linha 46 |
| F04-C02 | Arquivo inexistente. | Rejeita com AtualizacaoRecusada. Base e catálogo iguais. | AtualizacaoRecusada. Tabelas e catálogo iguais. | Aprovado | `test_f04_atualizacao.py`<br>`test_c02_arquivo_inexistente_e_recusado_e_base_preservada`<br>Anexo A, linha 47 |
| F04-C03 | Site fora do ar (sessão HTTP simulada). | Rejeita com AtualizacaoRecusada. Base e catálogo iguais. | AtualizacaoRecusada. Tabelas e catálogo iguais. | Aprovado | `test_f04_atualizacao.py`<br>`test_c03_site_fora_do_ar_e_recusado_e_base_preservada`<br>Anexo A, linha 48 |
| F04-C04 | Carga vazia. {"records": []}. | Rejeita. Base e catálogo iguais. | AtualizacaoRecusada. Tabelas e catálogo iguais. | Aprovado | `test_f04_atualizacao.py`<br>`test_c04_carga_sem_aulas_e_recusada`<br>Anexo A, linha 49 |
| F04-C05 | Formato inesperado. records como texto, sem a chave records, JSON que é só texto, arquivo que não é JSON. | Rejeita os quatro. Base e catálogo iguais. | AtualizacaoRecusada nos quatro. Tabelas e catálogo iguais. | Aprovado | `test_f04_atualizacao.py`<br>`test_c05_json_em_formato_inesperado_e_recusado`<br>Anexo A, linha 50 |
| F04-C06 | Acima do limite de recusas. 3 registros, 2 inválidos (início depois do fim; hora "xx"). | Rejeita informando "2 de 3 registros foram recusados". Base igual. | Mensagem esperada. Tabelas e catálogo iguais. | Aprovado | `test_f04_atualizacao.py`<br>`test_c06_mais_da_metade_recusada_e_rejeitada`<br>Anexo A, linha 51 |
| F04-C07 | Limite exato. 2 registros, 1 inválido. | Aceita: 2 lidos, 1 recusado; base passa a ter só AAA001. | (2, 1); base reaberta só com AAA001. | Aprovado | `test_f04_atualizacao.py`<br>`test_c07_metade_exata_recusada_ainda_e_aceita`<br>Anexo A, linha 52 |
| F04-C08 | Falha no meio da gravação. Gatilho no SQLite que aborta a inserção no histórico; carga da amostra. | Rejeita; a transação é desfeita e base e catálogo ficam iguais. | AtualizacaoRecusada. Tabelas e catálogo iguais. | Aprovado | `test_f04_atualizacao.py`<br>`test_c08_falha_ao_gravar_desfaz_tudo`<br>Anexo A, linha 53 |
| F04-C09 | Sequência. Grade ana com DCC011 TB e DCC024 TM; depois carga sem DCC011. | Aceita; linhas da grade iguais; DCC024 TM continua na grade e DCC011 TB aparece como ausente. | grade_turma igual; turmas [DCC024]; ausentes {DCC011: TB}. | Aprovado | `test_f04_atualizacao.py`<br>`test_c09_grades_sao_preservadas_e_turma_que_sumiu_fica_pendente`<br>Anexo A, linha 54 |
| F04-C10 | Carga repetida. O mesmo registros_teste.json. | Aceita; mesmos dados após reabrir; histórico com 2 cargas. | Catálogo igual ao inicial; 2 cargas no histórico. | Aprovado | `test_f04_atualizacao.py`<br>`test_c10_carga_igual_mantem_os_mesmos_dados`<br>Anexo A, linha 55 |

## 6. F05. Minha grade

**Regras verificadas.** Disciplina e turma precisam existir; uma turma por disciplina; no máximo 8 disciplinas e 8 itens por pedido; sem sobreposição de horário entre turmas da grade; pedido atendido por inteiro ou recusado por inteiro; nome de 1 a 40 caracteres (setter); identificação de 2 a 40 caracteres permitidos; gravação persistente.

**Preparação e estado inicial.** C01 a C15: base de teste com `registros_teste.json`; antes de cada teste, a grade "ana" recebe DCC011 TB (segunda e quarta, 09:25-11:05). C16 e C17: base de teste com `registros_grade_cheia.json` (TST001 a TST009, turma TA, cada uma num horário diferente) e grade "bia" vazia. C18 e C19: base com `registros_teste.json` e a conversa 42 do Telegram sem grade. Em C15, um gatilho no SQLite de teste força erro na gravação.

| ID | Regra e entrada | Resultado e estado final esperados | Resultado e estado final observados | Situação | Evidência |
|---|---|---|---|---|---|
| F05-C01 | Adicionar uma turma. ana, "dcc024 tm". | Aceita DCC024 TM; após reabrir, a grade tem DCC011 TB e DCC024 TM. | [(DCC024, TM)] devolvido; base reaberta com as duas turmas. | Aprovado | `test_f05_minha_grade.py`<br>`test_c01_adiciona_turma_e_grava`<br>Anexo A, linha 60 |
| F05-C02 | Várias turmas num pedido. "DCC024 TM; MAT038 TB1, MAT001 TOL1". | Aceita as três; grade com quatro disciplinas. | Grade com DCC011, DCC024, MAT001, MAT038. | Aprovado | `test_f05_minha_grade.py`<br>`test_c02_adiciona_varias_turmas_num_pedido`<br>Anexo A, linha 61 |
| F05-C03 | Conflito com turma salva. "DCC001 TB" (seg 09:25, igual a DCC011 TB). | Rejeita com ConflitoDeHorario. Grade e base iguais. | ConflitoDeHorario. Tabelas iguais; grade só com DCC011 TB. | Aprovado | `test_f05_minha_grade.py`<br>`test_c03_conflito_com_turma_salva_e_recusado`<br>Anexo A, linha 62 |
| F05-C04 | Conflito dentro do pedido. Grade nova "outro": "DCC024 TM; DCC001 TB; DCC011 TB". | Rejeita o pedido inteiro; DCC024 TM também não é gravada. | ConflitoDeHorario; grade "outro" com 0 disciplinas; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c04_conflito_no_pedido_recusa_todas_as_turmas`<br>Anexo A, linha 63 |
| F05-C05 | Disciplina inexistente no pedido. "DCC024 TM; XYZ999 TA". | Rejeita com NaoEncontrado; nada gravado. | NaoEncontrado; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c05_disciplina_inexistente_recusa_o_pedido_inteiro`<br>Anexo A, linha 64 |
| F05-C06 | Turma inexistente. "DCC024 TZ". | Rejeita com NaoEncontrado, listando "TE, TM". | Mensagem com "Turmas existentes: TE, TM"; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c06_turma_inexistente_e_recusada_com_as_turmas_validas`<br>Anexo A, linha 65 |
| F05-C07 | Disciplina já na grade. "DCC011 TE". | Rejeita com Duplicidade. | Duplicidade; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c07_disciplina_ja_na_grade_e_recusada`<br>Anexo A, linha 66 |
| F05-C08 | Repetida no pedido. "DCC024 TM; DCC024 TE". | Rejeita com Duplicidade. | Duplicidade; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c08_disciplina_repetida_no_pedido_e_recusada`<br>Anexo A, linha 67 |
| F05-C09 | Formato inválido. "", "  ;  ", "DCC024", "DCC024 TM extra". | Rejeita cada um com DadoInvalido. | DadoInvalido nos quatro; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c09_pedido_mal_formatado_e_recusado`<br>Anexo A, linha 68 |
| F05-C10 | Remover. " dcc011 ". | Remove DCC011; após reabrir, grade vazia. | Devolve DCC011; base reaberta com 0 disciplinas. | Aprovado | `test_f05_minha_grade.py`<br>`test_c10_remove_disciplina_e_grava`<br>Anexo A, linha 69 |
| F05-C11 | Remover disciplina fora da grade. "DCC024". | Rejeita com NaoEncontrado. | NaoEncontrado; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c11_remover_disciplina_fora_da_grade_e_recusado`<br>Anexo A, linha 70 |
| F05-C12 | Alterar nome (setter). "  Ana   Souza "; depois 40 caracteres. | Grava "Ana Souza"; aceita o limite de 40. | "Ana Souza" após reabrir; nome de 40 caracteres aceito. | Aprovado | `test_f05_minha_grade.py`<br>`test_c12_nome_valido_e_alterado_pelo_setter`<br>Anexo A, linha 71 |
| F05-C13 | Nome inválido. "", "   ", 41 caracteres. | Rejeita com DadoInvalido; nome anterior mantido. | DadoInvalido nos três; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c13_nome_vazio_ou_longo_e_recusado`<br>Anexo A, linha 72 |
| F05-C14 | Identificação inválida. "", "a", "Ana Maria", "joão", 41 caracteres. | Rejeita com DadoInvalido; nenhuma grade criada. | DadoInvalido nos cinco; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c14_identificacao_invalida_e_recusada`<br>Anexo A, linha 73 |
| F05-C15 | Falha ao gravar. Gatilho que aborta a inserção em grade_turma; "DCC024 TM". | Rejeita com GravacaoFalhou; grade igual. | GravacaoFalhou; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c15_falha_ao_gravar_preserva_a_grade`<br>Anexo A, linha 74 |
| F05-C16 | Limite de 8. Base de 9 disciplinas fictícias: 8 num pedido, depois a 9ª. | Aceita as 8; rejeita a 9ª com LimiteExcedido; base igual após a recusa. | 8 disciplinas; LimiteExcedido; base igual. | Aprovado | `test_f05_minha_grade.py`<br>`test_c16_oito_disciplinas_sao_aceitas_e_a_nona_e_recusada`<br>Anexo A, linha 58 |
| F05-C17 | Pedido com 9 itens. | Rejeita com DadoInvalido; grade vazia. | DadoInvalido; 0 disciplinas. | Aprovado | `test_f05_minha_grade.py`<br>`test_c17_pedido_com_nove_disciplinas_e_recusado`<br>Anexo A, linha 59 |
| F05-C18 | Sequência no bot. /minhagrade, /adicionar DCC011 TB; DCC024 TM, /minhagrade, /remover DCC011. | Grade vazia; confirmação das duas; grade com 2 disciplinas e a linha de DCC011 TB; confirmação da remoção. | Todas as respostas iguais às esperadas. | Aprovado | `test_f05_minha_grade.py`<br>`test_c18_fluxo_adicionar_ver_e_remover`<br>Anexo A, linha 56 |
| F05-C19 | Recusa no bot. /adicionar DCC001 TB após DCC011 TB; /remover sem argumento. | "Nada foi alterado." com o conflito; uso do /remover. | Respostas iguais às esperadas. | Aprovado | `test_f05_minha_grade.py`<br>`test_c19_recusa_no_bot_informa_que_nada_mudou`<br>Anexo A, linha 57 |

## 7. Verificações complementares

Estes testes não pertencem a uma única funcionalidade, mas verificam regras usadas por várias delas: os setters, a especialização `SalaOnline`, a regra de sobreposição, o polimorfismo das fontes e o menu do terminal. A lista completa está no Anexo A (arquivos `test_dominio.py`, `test_fontes.py` e `test_menu.py`); abaixo estão os principais.

| ID | Regra e entrada | Resultado esperado e observado | Situação | Evidência |
|---|---|---|---|---|
| D-01 | Setter de Sala.andar: 0 e None; depois -1, "2", 1.5 e True. | Aceita os dois primeiros; rejeita os demais mantendo o valor anterior. Observado igual. | Aprovado | `test_dominio.py`<br>`test_setter_do_andar_recusa_negativo_e_texto_sem_alterar`<br>Anexo A, linha 15 |
| D-02 | Sala.criar com prédio "on-line". | Cria SalaOnline, não presencial, sem andar e nunca livre. Observado igual. | Aprovado | `test_dominio.py`<br>`test_criar_devolve_a_especializacao_certa`<br>Anexo A, linha 11 |
| D-03 | Intervalos 09:25-11:05 e 11:05-12:45. | Não se sobrepõem; 11:04 já sobrepõe. Observado igual. | Aprovado | `test_dominio.py`<br>`test_intervalos_encostados_nao_se_sobrepoem`<br>Anexo A, linha 9 |
| D-04 | Turma com aulas sobrepostas no mesmo dia. | ConflitoDeHorario; turma continua com 1 aula. Observado igual. | Aprovado | `test_dominio.py`<br>`test_turma_nao_aceita_aulas_sobrepostas`<br>Anexo A, linha 10 |
| D-05 | GradeDoAluno com turmas encostadas (07:30-09:10 e 09:10-10:50). | Aceita as duas. Observado igual. | Aprovado | `test_dominio.py`<br>`test_turmas_encostadas_nao_conflitam`<br>Anexo A, linha 7 |
| D-06 | Três fontes concretas (arquivo, site simulado, base local). | Mesmos registros e mesmo catálogo pela mesma chamada coletar(). Observado igual. | Aprovado | `test_fontes.py`<br>`test_base_local_reconstroi_o_mesmo_catalogo_da_fonte_original`<br>Anexo A, linha 75 |
| D-07 | Menu: opções 4, ana, adicionar, conflito, renomear, ver. | Mensagens de sucesso e de recusa; menu continua. Observado igual. | Aprovado | `test_menu.py`<br>`test_minha_grade_pelo_menu`<br>Anexo A, linha 87 |
| D-08 | Menu: atualização por arquivo inexistente e origem inválida. | "A base anterior foi mantida." e "Origem inválida"; base igual. Observado igual. | Aprovado | `test_menu.py`<br>`test_atualizacao_recusada_pelo_menu_mantem_a_base`<br>Anexo A, linha 83 |

## 8. Defeitos e pendências

**Defeitos.** Nenhum defeito do código foi encontrado na última execução: os 85 testes foram aprovados.

**Erro na previsão, corrigido antes da última execução.** Na primeira versão do cenário F01-C07, o resultado esperado para "computadores" listava apenas DCC001 e DCC006. Na execução, o sistema devolveu também DCC017 (INTRODUCAO A ARQUITETURA DE COMPUTADORES). Conferindo a regra, a palavra "computadores" de fato aparece no nome de DCC017, então o comportamento estava correto e o erro era da previsão. O esperado foi corrigido para DCC001, DCC006 e DCC017, o cenário foi executado de novo junto com todos os demais testes da F01 e foi aprovado.

**Cenários não executados nesta verificação.**

| ID | Cenário | Motivo e situação |
|---|---|---|
| F04-C11 | Atualização pelo site real do ICEx (opção 1 do menu). | Não executado: o ambiente usado para os testes não alcança o site do ICEx. O comportamento de recusa foi coberto com a sessão simulada (F04-C03). Antes desta versão, o bot no Raspberry Pi já baixou a lista completa do site com a mesma classe `FonteIcexOnline` (997 registros), mas a versão 1.0.0 ainda não foi executada contra o site real. |
| F05-C20 | Comandos digitados no aplicativo do Telegram. | Não executado por unittest: os testes chamam `ComandosDoBot`, que recebe e devolve o mesmo texto do bot sem depender da biblioteca do Telegram (F01-C08, F02-C10, F03-C08, F05-C18). A camada `BotGuiaDeSalas`, que só repassa as mensagens, foi usada no Raspberry Pi com a versão anterior (/ajuda, /sala e /livres responderam corretamente); os comandos novos da versão 1.0.0 ainda não foram conferidos no aplicativo. |

## Anexo A. Saída da última execução

Execução de `python -m unittest discover -s tests -v` no conteúdo de `guia-salas-1.0.0.zip`, em 22/11/2026. Os números à esquerda são as linhas citadas na coluna Evidência. A mesma saída está em `docs/verificacao/execucao_unittest.txt` no repositório.

```text
  1  $ python --version
  2  Python 3.13.18
  3  $ python -m unittest discover -s tests -v
  4  test_conflito_no_pedido_nao_inclui_nenhuma_turma (test_dominio.TestGradeDoAluno.test_conflito_no_pedido_nao_inclui_nenhuma_turma) ... ok
  5  test_identificador_e_normalizado_e_somente_leitura (test_dominio.TestGradeDoAluno.test_identificador_e_normalizado_e_somente_leitura) ... ok
  6  test_setter_do_nome_valida_e_preserva_o_anterior (test_dominio.TestGradeDoAluno.test_setter_do_nome_valida_e_preserva_o_anterior) ... ok
  7  test_turmas_encostadas_nao_conflitam (test_dominio.TestGradeDoAluno.test_turmas_encostadas_nao_conflitam) ... ok
  8  test_inicio_depois_do_fim_e_recusado (test_dominio.TestIntervaloETurma.test_inicio_depois_do_fim_e_recusado) ... ok
  9  test_intervalos_encostados_nao_se_sobrepoem (test_dominio.TestIntervaloETurma.test_intervalos_encostados_nao_se_sobrepoem) ... ok
 10  test_turma_nao_aceita_aulas_sobrepostas (test_dominio.TestIntervaloETurma.test_turma_nao_aceita_aulas_sobrepostas) ... ok
 11  test_criar_devolve_a_especializacao_certa (test_dominio.TestSala.test_criar_devolve_a_especializacao_certa) ... ok
 12  test_sala_online_nunca_esta_livre_e_nao_tem_andar (test_dominio.TestSala.test_sala_online_nunca_esta_livre_e_nao_tem_andar) ... ok
 13  test_salas_com_mesma_chave_sao_iguais (test_dominio.TestSala.test_salas_com_mesma_chave_sao_iguais) ... ok
 14  test_setter_do_andar_aceita_inteiro_nao_negativo_ou_none (test_dominio.TestSala.test_setter_do_andar_aceita_inteiro_nao_negativo_ou_none) ... ok
 15  test_setter_do_andar_recusa_negativo_e_texto_sem_alterar (test_dominio.TestSala.test_setter_do_andar_recusa_negativo_e_texto_sem_alterar) ... ok
 16  test_c01_busca_por_nome_devolve_turmas_e_salas (test_f01_busca.TestF01Busca.test_c01_busca_por_nome_devolve_turmas_e_salas) ... ok
 17  test_c02_busca_por_codigo_ignora_maiusculas_e_espacos (test_f01_busca.TestF01Busca.test_c02_busca_por_codigo_ignora_maiusculas_e_espacos) ... ok
 18  test_c03_algarismo_equivale_a_romano_e_acentos_sao_ignorados (test_f01_busca.TestF01Busca.test_c03_algarismo_equivale_a_romano_e_acentos_sao_ignorados) ... ok
 19  test_c04_termo_com_tres_caracteres_e_aceito (test_f01_busca.TestF01Busca.test_c04_termo_com_tres_caracteres_e_aceito) ... ok
 20  test_c05_termo_curto_e_rejeitado_sem_alterar_catalogo (test_f01_busca.TestF01Busca.test_c05_termo_curto_e_rejeitado_sem_alterar_catalogo) ... ok
 21  test_c06_disciplina_ausente_devolve_resultado_vazio_valido (test_f01_busca.TestF01Busca.test_c06_disciplina_ausente_devolve_resultado_vazio_valido) ... ok
 22  test_c07_termo_comum_a_varias_disciplinas_devolve_todas (test_f01_busca.TestF01Busca.test_c07_termo_comum_a_varias_disciplinas_devolve_todas) ... ok
 23  test_c08_comando_sala_responde_e_nao_altera_a_base (test_f01_busca.TestF01ComandoDoBot.test_c08_comando_sala_responde_e_nao_altera_a_base) ... ok
 24  test_c09_comando_sala_com_termo_curto_mostra_exemplo (test_f01_busca.TestF01ComandoDoBot.test_c09_comando_sala_com_termo_curto_mostra_exemplo) ... ok
 25  test_c10_resposta_longa_e_dividida_entre_linhas (test_f01_busca.TestF01ComandoDoBot.test_c10_resposta_longa_e_dividida_entre_linhas) ... ok
 26  test_c10_livres_sem_andar_considera_todos_e_aceita_predio (test_f02_salas_livres.TestF02ComandoDoBot.test_c10_livres_sem_andar_considera_todos_e_aceita_predio) ... ok
 27  test_c11_livres_com_hora_invalida_mostra_motivo_e_uso (test_f02_salas_livres.TestF02ComandoDoBot.test_c11_livres_com_hora_invalida_mostra_motivo_e_uso) ... ok
 28  test_c12_livres_sem_hora_mostra_uso (test_f02_salas_livres.TestF02ComandoDoBot.test_c12_livres_sem_hora_mostra_uso) ... ok
 29  test_c01_sala_ocupada_nao_aparece (test_f02_salas_livres.TestF02SalasLivres.test_c01_sala_ocupada_nao_aparece) ... ok
 30  test_c02_sala_fica_livre_no_horario_de_termino (test_f02_salas_livres.TestF02SalasLivres.test_c02_sala_fica_livre_no_horario_de_termino) ... ok
 31  test_c03_sala_ocupada_no_horario_de_inicio (test_f02_salas_livres.TestF02SalasLivres.test_c03_sala_ocupada_no_horario_de_inicio) ... ok
 32  test_c04_turma_conjunta_ocupa_a_sala (test_f02_salas_livres.TestF02SalasLivres.test_c04_turma_conjunta_ocupa_a_sala) ... ok
 33  test_c05_aula_online_nunca_vira_sala_livre (test_f02_salas_livres.TestF02SalasLivres.test_c05_aula_online_nunca_vira_sala_livre) ... ok
 34  test_c06_predio_desconhecido_e_rejeitado_sem_alterar_catalogo (test_f02_salas_livres.TestF02SalasLivres.test_c06_predio_desconhecido_e_rejeitado_sem_alterar_catalogo) ... ok
 35  test_c07_andar_negativo_e_rejeitado (test_f02_salas_livres.TestF02SalasLivres.test_c07_andar_negativo_e_rejeitado) ... ok
 36  test_c08_hora_e_dia_invalidos_sao_rejeitados_na_conversao (test_f02_salas_livres.TestF02SalasLivres.test_c08_hora_e_dia_invalidos_sao_rejeitados_na_conversao) ... ok
 37  test_c09_andar_sem_salas_devolve_lista_vazia_valida (test_f02_salas_livres.TestF02SalasLivres.test_c09_andar_sem_salas_devolve_lista_vazia_valida) ... ok
 38  test_c01_planilha_de_exemplo_e_preenchida (test_f03_planilha.TestF03Planilha.test_c01_planilha_de_exemplo_e_preenchida) ... ok
 39  test_c02_turma_pedida_inexistente_vira_nao_localizada (test_f03_planilha.TestF03Planilha.test_c02_turma_pedida_inexistente_vira_nao_localizada) ... ok
 40  test_c03_arquivo_inexistente_e_recusado (test_f03_planilha.TestF03Planilha.test_c03_arquivo_inexistente_e_recusado) ... ok
 41  test_c04_extensao_diferente_de_xlsx_e_recusada (test_f03_planilha.TestF03Planilha.test_c04_extensao_diferente_de_xlsx_e_recusada) ... ok
 42  test_c05_arquivo_corrompido_e_recusado (test_f03_planilha.TestF03Planilha.test_c05_arquivo_corrompido_e_recusado) ... ok
 43  test_c06_planilha_sem_disciplinas_e_recusada (test_f03_planilha.TestF03Planilha.test_c06_planilha_sem_disciplinas_e_recusada) ... ok
 44  test_c07_saida_igual_a_entrada_e_recusada_e_original_preservado (test_f03_planilha.TestF03Planilha.test_c07_saida_igual_a_entrada_e_recusada_e_original_preservado) ... ok
 45  test_c08_comando_do_bot_devolve_legenda (test_f03_planilha.TestF03Planilha.test_c08_comando_do_bot_devolve_legenda) ... ok
 46  test_c01_carga_valida_substitui_a_base_e_registra_historico (test_f04_atualizacao.TestF04Atualizacao.test_c01_carga_valida_substitui_a_base_e_registra_historico) ... ok
 47  test_c02_arquivo_inexistente_e_recusado_e_base_preservada (test_f04_atualizacao.TestF04Atualizacao.test_c02_arquivo_inexistente_e_recusado_e_base_preservada) ... ok
 48  test_c03_site_fora_do_ar_e_recusado_e_base_preservada (test_f04_atualizacao.TestF04Atualizacao.test_c03_site_fora_do_ar_e_recusado_e_base_preservada) ... ok
 49  test_c04_carga_sem_aulas_e_recusada (test_f04_atualizacao.TestF04Atualizacao.test_c04_carga_sem_aulas_e_recusada) ... ok
 50  test_c05_json_em_formato_inesperado_e_recusado (test_f04_atualizacao.TestF04Atualizacao.test_c05_json_em_formato_inesperado_e_recusado) ... ok
 51  test_c06_mais_da_metade_recusada_e_rejeitada (test_f04_atualizacao.TestF04Atualizacao.test_c06_mais_da_metade_recusada_e_rejeitada) ... ok
 52  test_c07_metade_exata_recusada_ainda_e_aceita (test_f04_atualizacao.TestF04Atualizacao.test_c07_metade_exata_recusada_ainda_e_aceita) ... ok
 53  test_c08_falha_ao_gravar_desfaz_tudo (test_f04_atualizacao.TestF04Atualizacao.test_c08_falha_ao_gravar_desfaz_tudo) ... ok
 54  test_c09_grades_sao_preservadas_e_turma_que_sumiu_fica_pendente (test_f04_atualizacao.TestF04Atualizacao.test_c09_grades_sao_preservadas_e_turma_que_sumiu_fica_pendente) ... ok
 55  test_c10_carga_igual_mantem_os_mesmos_dados (test_f04_atualizacao.TestF04Atualizacao.test_c10_carga_igual_mantem_os_mesmos_dados) ... ok
 56  test_c18_fluxo_adicionar_ver_e_remover (test_f05_minha_grade.TestF05ComandosDoBot.test_c18_fluxo_adicionar_ver_e_remover) ... ok
 57  test_c19_recusa_no_bot_informa_que_nada_mudou (test_f05_minha_grade.TestF05ComandosDoBot.test_c19_recusa_no_bot_informa_que_nada_mudou) ... ok
 58  test_c16_oito_disciplinas_sao_aceitas_e_a_nona_e_recusada (test_f05_minha_grade.TestF05LimiteDaGrade.test_c16_oito_disciplinas_sao_aceitas_e_a_nona_e_recusada) ... ok
 59  test_c17_pedido_com_nove_disciplinas_e_recusado (test_f05_minha_grade.TestF05LimiteDaGrade.test_c17_pedido_com_nove_disciplinas_e_recusado) ... ok
 60  test_c01_adiciona_turma_e_grava (test_f05_minha_grade.TestF05MinhaGrade.test_c01_adiciona_turma_e_grava) ... ok
 61  test_c02_adiciona_varias_turmas_num_pedido (test_f05_minha_grade.TestF05MinhaGrade.test_c02_adiciona_varias_turmas_num_pedido) ... ok
 62  test_c03_conflito_com_turma_salva_e_recusado (test_f05_minha_grade.TestF05MinhaGrade.test_c03_conflito_com_turma_salva_e_recusado) ... ok
 63  test_c04_conflito_no_pedido_recusa_todas_as_turmas (test_f05_minha_grade.TestF05MinhaGrade.test_c04_conflito_no_pedido_recusa_todas_as_turmas) ... ok
 64  test_c05_disciplina_inexistente_recusa_o_pedido_inteiro (test_f05_minha_grade.TestF05MinhaGrade.test_c05_disciplina_inexistente_recusa_o_pedido_inteiro) ... ok
 65  test_c06_turma_inexistente_e_recusada_com_as_turmas_validas (test_f05_minha_grade.TestF05MinhaGrade.test_c06_turma_inexistente_e_recusada_com_as_turmas_validas) ... ok
 66  test_c07_disciplina_ja_na_grade_e_recusada (test_f05_minha_grade.TestF05MinhaGrade.test_c07_disciplina_ja_na_grade_e_recusada) ... ok
 67  test_c08_disciplina_repetida_no_pedido_e_recusada (test_f05_minha_grade.TestF05MinhaGrade.test_c08_disciplina_repetida_no_pedido_e_recusada) ... ok
 68  test_c09_pedido_mal_formatado_e_recusado (test_f05_minha_grade.TestF05MinhaGrade.test_c09_pedido_mal_formatado_e_recusado) ... ok
 69  test_c10_remove_disciplina_e_grava (test_f05_minha_grade.TestF05MinhaGrade.test_c10_remove_disciplina_e_grava) ... ok
 70  test_c11_remover_disciplina_fora_da_grade_e_recusado (test_f05_minha_grade.TestF05MinhaGrade.test_c11_remover_disciplina_fora_da_grade_e_recusado) ... ok
 71  test_c12_nome_valido_e_alterado_pelo_setter (test_f05_minha_grade.TestF05MinhaGrade.test_c12_nome_valido_e_alterado_pelo_setter) ... ok
 72  test_c13_nome_vazio_ou_longo_e_recusado (test_f05_minha_grade.TestF05MinhaGrade.test_c13_nome_vazio_ou_longo_e_recusado) ... ok
 73  test_c14_identificacao_invalida_e_recusada (test_f05_minha_grade.TestF05MinhaGrade.test_c14_identificacao_invalida_e_recusada) ... ok
 74  test_c15_falha_ao_gravar_preserva_a_grade (test_f05_minha_grade.TestF05MinhaGrade.test_c15_falha_ao_gravar_preserva_a_grade) ... ok
 75  test_base_local_reconstroi_o_mesmo_catalogo_da_fonte_original (test_fontes.TestFonteBancoLocal.test_base_local_reconstroi_o_mesmo_catalogo_da_fonte_original) ... ok
 76  test_arquivo_inexistente_lanca_fonte_indisponivel (test_fontes.TestFontes.test_arquivo_inexistente_lanca_fonte_indisponivel) ... ok
 77  test_arquivo_inexistente_vira_falha_no_relatorio (test_fontes.TestFontes.test_arquivo_inexistente_vira_falha_no_relatorio) ... ok
 78  test_atualizador_monta_o_mesmo_catalogo_com_qualquer_fonte (test_fontes.TestFontes.test_atualizador_monta_o_mesmo_catalogo_com_qualquer_fonte) ... ok
 79  test_duas_fontes_concretas_entregam_os_mesmos_registros (test_fontes.TestFontes.test_duas_fontes_concretas_entregam_os_mesmos_registros) ... ok
 80  test_separacao_de_predio_e_sala (test_fontes.TestFontes.test_separacao_de_predio_e_sala) ... ok
 81  test_abertura_mostra_a_base_e_a_ultima_atualizacao (test_menu.TestMenu.test_abertura_mostra_a_base_e_a_ultima_atualizacao) ... ok
 82  test_andar_nao_numerico_e_recusado_e_menu_continua (test_menu.TestMenu.test_andar_nao_numerico_e_recusado_e_menu_continua) ... ok
 83  test_atualizacao_recusada_pelo_menu_mantem_a_base (test_menu.TestMenu.test_atualizacao_recusada_pelo_menu_mantem_a_base) ... ok
 84  test_busca_pelo_menu (test_menu.TestMenu.test_busca_pelo_menu) ... ok
 85  test_fim_da_entrada_encerra_sem_erro (test_menu.TestMenu.test_fim_da_entrada_encerra_sem_erro) ... ok
 86  test_hora_invalida_e_opcao_invalida (test_menu.TestMenu.test_hora_invalida_e_opcao_invalida) ... ok
 87  test_minha_grade_pelo_menu (test_menu.TestMenu.test_minha_grade_pelo_menu) ... ok
 88  test_planilha_pelo_menu (test_menu.TestMenu.test_planilha_pelo_menu) ... ok
 89  
 90  ----------------------------------------------------------------------
 91  Ran 85 tests in 0.772s
 92  
 93  OK
```
