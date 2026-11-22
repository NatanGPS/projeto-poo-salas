# Pendências e informações necessárias

Itens que dependem de decisão ou de verificação fora do código.

## Dados do ICEx

O bot lê `https://www.icex.ufmg.br/minhasala/recupera_salas.php`, o mesmo JSON que a página do ICEx usa (`{"records": [...]}`, cerca de 420 aulas, com `nome_materia`, `codigo_materia`, `turma`, `hora_inicial`, `hora_final`, `dia_semana`, `nome_sala`).

Os testes e as entregas usam uma amostra real de 110 registros (`guia_salas/dados/amostra_icex.json`), consultada em 15/10/2026, com disciplinas de MAT, DCC e EST. A lista completa não foi carregada aqui; para conferir quando quiser, rode `python scripts/baixar_dados_icex.py`.

## O que a amostra real mostrou

- **Turmas conjuntas existem.** DCC006-TL1 e DCC017-TN dividem a sala 407 do CAD3 no mesmo horário, e há turmas como "TM2/ TN3". A regra foi ajustada para aceitar esses casos.
- **Salas fora do ICEx.** O quadro inclui CAD1, CAD2, CAD3, auditórios ("AUD. II - ICEX") e aulas "ON-LINE".
- **Programação Orientada a Objetos não aparece no quadro do ICEx.**

## Decisões de regra ainda abertas

| Dúvida | Situação atual no código |
|---|---|
| `dia_semana` como `Seg-Sex` significa segunda e sexta ou segunda a sexta? | Lido como lista (segunda e sexta), coerente com MAT001-TE1 |
| Turmas conjuntas devem aparecer juntas na resposta? | Cada turma aparece separada |
| Abreviações ("BD", "GAAL") | Não reconhecidas |
| Mínimo de 3 caracteres no termo de busca | Em vigor |
| Mostrar todas as turmas ou só a do aluno (MAT001 tem 24) | Mostra todas; respostas longas são divididas em várias mensagens |
| Salas sem nenhuma aula não aparecem como livres | Só são conhecidas as salas que aparecem no quadro |
| Grade enviada como imagem | O bot pede uma planilha .xlsx |
| Frequência da atualização da base | 60 minutos (`GUIA_SALAS_INTERVALO_MIN`) |

## Fora do escopo nesta fase

- Consulta de salas da Escola de Engenharia (https://alocacao.eng.ufmg.br/consulta.html): o endereço dos dados não foi identificado. A interface `FonteDeDados` permite incluí-la depois.
