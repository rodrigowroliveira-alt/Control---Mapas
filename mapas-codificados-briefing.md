# Mapas Codificados — briefing para desenvolvimento (v1)

Módulo do Control para montar, preencher e comparar mapas de quantidades codificados (o que hoje é feito em planilhas Excel tipo "Quadro de Concorrência"). Este documento é o ponto de partida para começar a implementação — os fundamentos já foram discutidos e decididos; o que estiver em "Perguntas em aberto" ainda precisa de decisão antes ou durante o desenvolvimento.

## Contexto / por que isso existe

O modelo atual é uma planilha Excel por obra/escopo (ex.: `QC_195_ALUMÍNIO`), com um item codificado por linha (`AL001`, `GC01A`, `PT03`...), colunas de quantidade/preço repetidas para cada fornecedor, e fórmulas célula a célula. Na prática isso gera problemas recorrentes:

- Códigos digitados de forma inconsistente entre documentos (`AL36` vs. `AL036`), quebrando comparações automáticas.
- Descrição colada por engano de uma linha pra outra (copy-paste), ficando errada em várias linhas sem ninguém notar.
- Itens duplicados por engano dentro da própria proposta de um fornecedor, inflando o total sem ninguém perceber.
- Estado "não orçado" representado com célula mesclada + texto, o que torna a planilha frágil para editar (fácil de corromper mesclagem/fórmula) e impossível de tratar como dado estruturado.
- Fórmulas soltas por célula, que quebram silenciosamente (`#VALUE!`, range desatualizado) sem ninguém perceber até alguém abrir o arquivo.
- Comparar uma proposta nova com o que já está na planilha é trabalho manual, item por item.

O objetivo do sistema é resolver isso: dado estruturado em vez de célula solta, cálculo garantido pelo sistema em vez de fórmula manual, e exportação (PDF/XLS) gerada a partir do dado — não o contrário.

## Quem usa

Só funcionários internos (acessam pelo Control). **O fornecedor não usa o sistema.** O fluxo real é: o engenheiro solicita orçamento ao fornecedor por e-mail → o fornecedor responde por e-mail (PDF/planilha própria) → um funcionário interno lança essa cotação no sistema. Não há login nem portal externo para fornecedor no v1 (e provavelmente nunca — não é objetivo do projeto).

## Modelo de dados

Catálogo de itens é **por obra**, não global entre obras (decisão já tomada — cada obra tem seus próprios itens codificados, sem reaproveitamento automático entre obras diferentes).

### Obra
| Campo | Tipo | Observação |
|---|---|---|
| id | string/uuid | |
| nome | string | |
| endereço | string | opcional |
| criado_em | datetime | |

### Mapa
Um mapa = um escopo dentro de uma obra (ex.: "Esquadrias de Alumínio", "Guarda-corpo").

| Campo | Tipo | Observação |
|---|---|---|
| id | string/uuid | |
| obra_id | fk → Obra | |
| nome | string | |
| status | enum | `rascunho` \| `em_cotacao` \| `fechado` — fluxo de aprovação ainda não definido, ver "Perguntas em aberto" |
| criado_em | datetime | |

### Item
Pertence a um Mapa. É a linha codificada (o que hoje é `AL001`, `GC01A` etc.).

| Campo | Tipo | Observação |
|---|---|---|
| id | string/uuid | |
| mapa_id | fk → Mapa | |
| codigo | string | **único dentro do mapa** — validar na gravação, sem exceção |
| descricao | string | |
| unidade | string | ex.: `unid`, `m`, `m²` |
| quantidade_referencia | number | quantitativo do projeto para aquele item; pode ficar em branco se ainda não medido (não usar texto tipo "—" ou "ver obra" — ver regras abaixo) |

### Fornecedor
Cadastro simples, reutilizável entre mapas e obras (empresa que a construtora cota com frequência). Editável pelo operador a qualquer momento — não é só criado uma vez, é corrigido/completado conforme os dados chegam. Campos além de nome/contato/telefone/email vieram do arquivo Excel real e servem de base para um futuro cadastro/banco de dados de suprimentos (decisão de 2026-09-01).

| Campo | Tipo | Observação |
|---|---|---|
| id | string/uuid | |
| nome | string | |
| contato | string | opcional |
| telefone / email | string | opcional |
| endereco | string | opcional |
| cidade | string | opcional |
| cnpj | string | opcional, **sem validação de formato/duplicidade no v1** — ver "Perguntas em aberto" |
| inscricao_estadual | string | opcional |
| socio | string | opcional |

### Cotação
A resposta de um Fornecedor para um Item específico de um Mapa. **A ausência de registro = item não orçado por aquele fornecedor** (não existe estado "NÃO ORÇADO" como texto — é simplesmente a ausência da linha).

| Campo | Tipo | Observação |
|---|---|---|
| id | string/uuid | |
| item_id | fk → Item | |
| fornecedor_id | fk → Fornecedor | |
| quantidade | number | pode divergir da quantidade_referencia do item — é esperado, não é erro |
| preco_unitario | number | |
| total | number | **calculado** = quantidade × preco_unitario, nunca digitado |
| observacao | string | opcional |
| lancado_em | datetime | |

## Regras de negócio

- Código de item é único dentro do mapa. Bloquear gravação com mensagem clara se duplicar.
- Alertar (não bloquear) se dois itens do mesmo mapa tiverem descrição muito parecida + mesma quantidade — possível duplicidade a revisar manualmente (foi um problema real encontrado).
- Total da cotação é sempre calculado pelo sistema, nunca um campo editável diretamente.
- Subtotal por fornecedor num mapa = soma dos totais de todas as cotações daquele fornecedor naquele mapa.
- "Melhor valor" por item = menor total entre os fornecedores que cotaram aquele item (ignora quem não cotou; não trata ausência como zero).
- Quantidade de referência do item pode ficar vazia (ainda não medida) — nesse caso não entra em nenhum cálculo de "melhor valor total esperado", só fica sinalizada como pendente na tela.
- **Mínimo de 3 fornecedores cotando por mapa** (decisão de 2026-09-01, atualiza o v1 original que previa 2). Vale tanto para gerar a exportação PDF/XLS de comparação final quanto para fechar o mapa (status → `fechado`). Um mapa pode ter itens cadastrados e cotações lançadas com menos de 3 fornecedores normalmente — o bloqueio é só na exportação final e no fechamento.

## Fluxo de uso

1. Funcionário cria a Obra (se ainda não existir) e cria um Mapa dentro dela.
2. Cadastra os itens do mapa: código, descrição, unidade, quantidade de referência (a partir do projeto/quantitativo).
3. Conforme as respostas dos fornecedores chegam por e-mail, o funcionário cadastra o Fornecedor (se novo) e lança a cotação dele, item por item.
4. A qualquer momento, a tela de comparação mostra todos os fornecedores lado a lado, com total, subtotal e melhor valor calculados.
5. Exporta PDF e/ou XLS quando precisar levar isso pra decisão ou arquivo.

## Telas / funcionalidades do v1

- **Cadastro de mapa**: nome, obra, status.
- **Cadastro de itens**: lista editável do mapa (código, descrição, unidade, quantidade de referência), com validação de código único.
- **Lançamento de cotação**: escolher fornecedor (ou cadastrar novo) e preencher quantidade + preço por item; total calculado em tempo real.
- **Tela de comparação**: itens em linha, um bloco de colunas (quantidade/preço/total) por fornecedor, subtotal por fornecedor, melhor valor por item destacado.
- **Exportar PDF**: dois formatos —
  - *Comparação*: todos os fornecedores lado a lado (uso interno).
  - *Solicitação*: só itens + quantidade de referência, sem preço — para anexar no e-mail pedindo cotação a um fornecedor novo (não é essencial no v1, mas é barato de fazer já que os dados são os mesmos da tela de cadastro de itens).
- **Exportar XLS**: tabela simples (sem célula mesclada), uma linha por item, colunas repetidas por fornecedor; manter fórmula de total visível na célula (`=quantidade×preço`) para quem for conferir manualmente.

### Estrutura do XLS validada contra arquivo real (2026-09-01)

O layout de colunas foi conferido contra `Azo_QC_195_ALUMÍNIO_rev4.xlsx`
(aba `QC0003`), o próprio `QC_195_ALUMÍNIO` citado no contexto acima. Ordem
final: `Item` (nº sequencial) / `Código` / `Descrição` / `Unidade` /
`Qtd. Referência`, depois um bloco `Quant.` / `Custo Unitário` / `Total`
por fornecedor, e por fim `Melhor Valor Unitário` / `Melhor Valor Total`
(menor custo unitário entre quem cotou × quantidade de referência — fica
em branco se a quantidade de referência ainda não foi medida ou se
ninguém cotou, mesma regra de "não entra em cálculo, só fica pendente").

O arquivo real confirmou, com dado de produção, os 3 problemas que
motivaram o projeto: fórmula de "melhor valor" quebrada em uma linha por
referenciar a coluna errada, descrição colada do lugar errado em 4 linhas
seguidas, e uma nota manual reportando item duplicado dentro da própria
proposta de um fornecedor. Também confirmou que "NÃO ORÇADO" é hoje texto
mesclado entre as 3 colunas do fornecedor — decidiu-se **não** reproduzir
isso na exportação (mantém célula vazia, decisão já tomada acima).

Ficaram de fora do v1 (ver "Fora de escopo" abaixo) os blocos que o
arquivo real também tem mas que pertencem ao controle orçamentário do
Control, não ao Mapa em si: ligação de cada item com centro de
custo/insumo/saldo orçamentário disponível, condições comerciais do
fornecedor vencedor (prazo de entrega, condição de pagamento, frete,
validade da proposta) e indexador INCC/verba meta para atualização
monetária do orçamento.

## Fora de escopo no v1

- Qualquer integração com PCP/CCP ou outros módulos do Control — mapa é isolado por enquanto. Isso inclui os blocos de saldo orçamentário/centro de custo/insumo, condições comerciais do vencedor e indexador INCC/verba meta que existem no arquivo Excel real da empresa, mas pertencem ao controle orçamentário, não ao Mapa.
- Login ou portal para fornecedor preencher a própria cotação.
- Importação automática de PDF/planilha de proposta recebida (reconhecer itens e preencher cotação sozinho). É uma boa ideia de fase 2 — reduziria exatamente o trabalho manual de digitar cotação item por item — mas não é essencial para validar o v1.
- Fluxo de aprovação/assinatura do mapa antes de virar contrato (ver pergunta em aberto abaixo).

## Perguntas em aberto

- **Quem aprova/fecha um mapa antes dele virar contrato?** Existe uma pessoa (ex.: engenheiro responsável) que precisa validar antes do status virar `fechado`, ou qualquer funcionário com acesso pode fechar? Isso define se precisa de um campo tipo `aprovado_por` / `aprovado_em` já no v1 ou se fica só como o campo `status` por enquanto.
- O cadastro de Fornecedor é livre (qualquer funcionário cadastra um novo a qualquer momento) ou precisa de alguma validação/duplicidade (CNPJ, por exemplo) antes de virar um registro novo?

## Sugestões técnicas (não vinculante)

Se o Control já tem uma stack definida, usar a mesma por consistência — isso tem prioridade sobre qualquer sugestão abaixo.

- Banco relacional simples é suficiente (o modelo de dados acima é pequeno e bem definido); não há necessidade de nada além disso no v1.
- Geração de PDF e XLS a partir do mesmo dado estruturado (não gerar um a partir do outro) — evita os dois ficarem divergentes.
- XLS exportado não deve usar células mescladas para representar "não orçado" — deixar a célula vazia é suficiente e evita a fragilidade descrita no contexto.

## Critérios de aceite do v1

- [ ] Criar obra, criar mapa, cadastrar itens com código único (bloqueia duplicado).
- [ ] Cadastrar fornecedor e lançar cotação por item; total calculado automaticamente.
- [ ] Tela de comparação mostra todos os fornecedores lado a lado com subtotal e melhor valor corretos.
- [ ] Exportar PDF (comparação) e XLS a partir de um mapa com pelo menos 3 fornecedores cotando (bloquear com mensagem clara se houver menos).
- [ ] Duplicar um código de item existente no mesmo mapa é bloqueado com mensagem clara.
