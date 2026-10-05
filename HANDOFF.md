# Handoff — Control / Mapas

Registro para quem for continuar o projeto (troca de acesso/conta). Data: 05/10/2026.

## Onde o projeto está

- **Repositório:** `rodrigowroliveira-alt/Control---Mapas` (GitHub).
- **Fase:** especificação do v1 concluída. **Nenhum código escrito ainda.**
- **Commits até aqui:** commit inicial + upload do briefing (`mapas-codificados-briefing.md`) e da planilha de referência (`Azo_-_QC_195_-_ALUMÍNIO_-_rev4.xlsx`) + este README/HANDOFF.

## Decisões já tomadas (não reabrir)

1. **Só usuários internos.** Fornecedor não usa o sistema; proposta chega por e-mail e é lançada por um funcionário. Sem portal/login de fornecedor.
2. **Catálogo de itens por obra**, não global.
3. **"Não orçado" = ausência de registro de cotação.** Nada de texto "NÃO ORÇADO" nem célula mesclada.
4. **Total sempre calculado** (quantidade × preço unitário), nunca editável.
5. **Código de item único dentro do mapa** — bloqueio na gravação.
6. **Quantidade cotada pode divergir da quantidade de referência** — é esperado, não é erro.
7. **PDF e XLS gerados do mesmo dado estruturado**, nunca um a partir do outro. XLS sem células mescladas e com fórmula de total visível.
8. **Stack:** usar a do Control.

## Perguntas em aberto (decidir antes/durante o desenvolvimento)

- [ ] Quem aprova/fecha o mapa (status `fechado`)? Precisa de `aprovado_por` / `aprovado_em` já no v1?
- [ ] Cadastro de fornecedor é livre ou precisa validar duplicidade (ex.: CNPJ)?
- [ ] Qual é a stack do Control (linguagem, framework, banco) — confirmar antes de criar o projeto.

## Fora de escopo no v1

- Integração com PCP/CCP e outros módulos do Control.
- Portal/login de fornecedor.
- Importação automática de PDF/planilha de proposta (candidata a fase 2).
- Fluxo de aprovação/assinatura do mapa.

## Próximos passos sugeridos

1. Responder as perguntas em aberto acima.
2. Confirmar a stack do Control e criar a estrutura do projeto.
3. Implementar o modelo de dados (Obra, Mapa, Item, Fornecedor, Cotação) com as validações.
4. Telas: cadastro de mapa → cadastro de itens → lançamento de cotação → comparação.
5. Exportações: XLS e PDF de comparação; PDF de solicitação se sobrar tempo.
6. Validar com a planilha `QC_195_ALUMÍNIO rev4` como massa de teste: importar os itens e cotações e conferir se subtotais e melhor valor batem com a planilha (descontando os erros já conhecidos dela — códigos inconsistentes, descrições coladas erradas, itens duplicados).

## Critérios de aceite do v1

- [ ] Criar obra, mapa e itens com código único (duplicado bloqueado com mensagem clara).
- [ ] Cadastrar fornecedor e lançar cotação por item; total automático.
- [ ] Comparação lado a lado com subtotal e melhor valor corretos.
- [ ] Exportar PDF (comparação) e XLS de um mapa com pelo menos 2 fornecedores.

## Como retomar no novo acesso

1. Ter acesso ao repositório no GitHub (adicionar a nova conta como colaborador, se for outra conta).
2. Clonar: `git clone https://github.com/rodrigowroliveira-alt/Control---Mapas.git`
3. Ler `README.md` → `HANDOFF.md` → `mapas-codificados-briefing.md`.
4. Ao abrir uma nova sessão com o Claude, pedir: *"Leia o HANDOFF.md e o briefing e vamos começar o v1."*
