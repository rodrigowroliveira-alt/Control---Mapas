# Control---Mapas
Sistema de Criação de Mapas de Concorrência

Modelo de dados e regras de negócio: ver `mapas-codificados-briefing.md`.

## Protótipo (`mapas_control/`)

Protótipo Python standalone do módulo, para validar modelo de dados, regras
de negócio e exportação PDF/XLS antes da integração no Control.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pytest mapas_control/tests -q   # testes das regras de negócio
python -m mapas_control.demo              # gera exemplo em output/
```

Regra vigente: um mapa precisa de no mínimo **3 fornecedores cotando** para
gerar a exportação PDF/XLS de comparação final ou para ser fechado
(`services/regras.py::MIN_FORNECEDORES_MAPA`).

A estrutura do XLSX exportado (`export/xlsx_export.py`) foi validada contra o
arquivo real da empresa (`Azo_QC_195_ALUMÍNIO_rev4.xlsx`, aba `QC0003`):
`Item`/`Código`/`Descrição`/`Unidade`/`Qtd. Referência` + bloco `Quant.` /
`Custo Unitário` / `Total` por fornecedor + `Melhor Valor Unitário` /
`Melhor Valor Total`. Por decisão de 2026-09-01, ficaram de fora do v1 os
blocos extras que existem no arquivo real mas pertencem ao controle
orçamentário do Control, não ao Mapa (ligação com centro de
custo/insumo/saldo disponível, condições comerciais do vencedor, indexador
INCC/verba meta) — ver `mapas-codificados-briefing.md`.

## Frontend web (`mapas_control/web/`)

Aplicação FastAPI + Jinja2 + htmx (server-rendered, sem SPA/API JSON
separada) implementando o fluxo Obras → Mapas → detalhe do Mapa (abas
Itens / Fornecedores & Cotações / Comparação) em cima do mesmo backend
acima, sem duplicar nenhuma regra de negócio.

```bash
python -m mapas_control.web.seed             # popula mapas_control.db com dado de exemplo (idempotente)
uvicorn mapas_control.web.main:app --reload  # http://127.0.0.1:8000
```

`mapas_control.db` (SQLite on-disk, gitignored) é criado automaticamente no
primeiro request. Sem autenticação nesta fase — assume que será plugado no
Control de verdade depois.
