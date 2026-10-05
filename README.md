# Control — Mapas

Sistema de criação de **Mapas de Concorrência** (quadros de cotação codificados) do Control.

Hoje esses mapas são feitos em planilhas Excel tipo "Quadro de Concorrência" (ex.: `QC_195_ALUMÍNIO`). Este módulo substitui a planilha por dado estruturado: itens codificados por mapa, cotações por fornecedor, totais calculados pelo sistema e exportação para PDF/XLS a partir do mesmo dado.

## Status do projeto

**Fase: especificação concluída — implementação ainda não iniciada.**

Ainda não existe código. O repositório contém apenas a especificação e um exemplo real da planilha atual.

## Conteúdo do repositório

| Arquivo | O que é |
|---|---|
| `README.md` | Este arquivo — visão geral do projeto. |
| `mapas-codificados-briefing.md` | Briefing completo do v1: contexto, modelo de dados, regras de negócio, telas, fora de escopo, perguntas em aberto e critérios de aceite. **Ponto de partida para desenvolver.** |
| `HANDOFF.md` | Registro de passagem de bastão: onde o projeto parou, decisões tomadas e próximos passos. |
| `Azo_-_QC_195_-_ALUMÍNIO_-_rev4.xlsx` | Planilha real do processo atual (QC 195 — Esquadrias de Alumínio, rev4), usada como referência dos problemas a resolver e como massa de teste. |

## Resumo do v1

**Usuários:** apenas funcionários internos, via Control. Fornecedor não acessa o sistema — envia a proposta por e-mail e um funcionário lança a cotação.

**Entidades:**

- **Obra** → possui vários **Mapas** (um mapa = um escopo, ex.: "Esquadrias de Alumínio").
- **Mapa** → possui vários **Itens** codificados (`AL001`, `GC01A`, …). Catálogo de itens é **por obra**, sem reaproveitamento entre obras.
- **Fornecedor** → cadastro reutilizável entre mapas e obras.
- **Cotação** → preço de um fornecedor para um item. Ausência de cotação = "não orçado".

**Regras principais:**

- Código de item é único dentro do mapa (bloqueia gravação).
- Alerta (sem bloquear) para itens com descrição muito parecida e mesma quantidade.
- Total = quantidade × preço unitário, sempre calculado, nunca digitado.
- Melhor valor por item = menor total entre quem cotou (ausência não conta como zero).

**Funcionalidades:** cadastro de mapa e itens, lançamento de cotação, tela de comparação lado a lado, exportação PDF (comparação e solicitação) e XLS (sem células mescladas).

Detalhes completos em [`mapas-codificados-briefing.md`](mapas-codificados-briefing.md).

## Stack

Ainda não definida. Regra: **usar a mesma stack do Control** por consistência. Na falta dela, um banco relacional simples atende o v1.

## Como continuar

Leia `HANDOFF.md` e depois `mapas-codificados-briefing.md`.
