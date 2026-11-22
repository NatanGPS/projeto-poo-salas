# Pendências e decisões abertas

Situação na versão 1.0.0 (produto final).

## Dados do ICEx

O sistema lê `https://www.icex.ufmg.br/minhasala/recupera_salas.php`, o mesmo JSON que a página do ICEx usa (`{"records": [...]}`, com `nome_materia`, `codigo_materia`, `turma`, `hora_inicial`, `hora_final`, `dia_semana`, `nome_sala`). No Raspberry Pi, a carga completa trouxe 997 registros.

A entrega usa uma amostra real de 110 registros (`guia_salas/dados/amostra_icex.json`), consultada em 15/10/2026, com disciplinas de MAT, DCC e EST.

## Decisões de regra ainda abertas

| Dúvida | Situação atual no código |
|---|---|
| `dia_semana` como `Seg-Sex` significa segunda e sexta ou segunda a sexta? | Lido como lista (segunda e sexta), coerente com MAT001-TE1 |
| Turmas conjuntas devem aparecer juntas na resposta? | Cada turma aparece separada |
| Abreviações ("BD", "GAAL") | Não reconhecidas |
| Mínimo de 3 caracteres no termo de busca | Em vigor |
| Salas sem nenhuma aula não aparecem como livres | Só são conhecidas as salas que aparecem no quadro |
| Limite de 8 disciplinas na grade do aluno | Em vigor; valor escolhido pelo grupo, sem norma da UFMG |
| Aula on-line conta como conflito na grade | Sim: o aluno não pode estar em duas aulas ao mesmo tempo |
| Atualização recusada quando mais da metade dos registros é inválida | Em vigor (`PROPORCAO_MINIMA_ACEITA = 0.5`) |

## Fora do escopo nesta versão

- Escola de Engenharia (https://alocacao.eng.ufmg.br/consulta.html): o endereço dos dados não foi identificado. A interface `FonteDeDados` permite incluí-la como nova subclasse.
- Grade enviada como imagem: exigiria reconhecimento de texto (OCR); o sistema aceita planilha .xlsx.
