# Solicitação de orçamento — Impermeabilização (Península RJ - Fase A)

Resumo da planilha de quantitativo **IMP-LO-121-PLA-R03** (3.677 linhas, 295 ambientes) em um formulário de
cotação com **21 preços a preencher** pelo empreiteiro.

## Estrutura escolhida
- **Preço por tipo de sistema** (código do projeto: I20EL, M44A, M44AR05…), em R$/m² de sistema completo,
  separado em material e mão de obra. Os 16 sistemas do projeto viram 16 itens.
- **Serviços complementares cotados em separado** (CP01 regularização, CP02 proteção mecânica horizontal,
  CP03 proteção mecânica vertical, CP04 proteção armada em concreto, CP05 drenagem) — é o que mais varia entre
  propostas (um inclui, outro não), então separar é o que torna a equalização possível.
- **Pavimento e bloco são distribuição, não preço**: a aba *Qtd por Pavimento* multiplica as quantidades de cada
  pavimento/bloco pelo preço unitário da proposta. O empreiteiro não precisa preencher nada por pavimento.
- **Opcional piscina** separado, usando os mesmos preços unitários.

## Abas
| Aba | Conteúdo |
|---|---|
| Instruções | Como preencher, legenda de cores |
| Proposta | Formulário do fornecedor (células amarelas) |
| Qtd por Pavimento | m² e R$ por pavimento (5) e por bloco (A/B/C) — SUMIFS sobre a Memória |
| Memória por Ambiente | 1 linha por ambiente, com a linha de origem na R03 |
| Especificação dos Sistemas | Descrição completa de cada código |
| Pendências | Erros encontrados na R03 |

## Ligação com o módulo de Mapas
Cada linha da aba *Proposta* corresponde a um **Item** do mapa (`codigo` = código do sistema/CPxx,
`unidade` = m², `quantidade_referencia` = coluna Quantidade). Cada proposta recebida vira um conjunto de
**Cotações** (quantidade × preço unitário) desse fornecedor.
