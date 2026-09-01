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

A estrutura do XLSX exportado (`export/xlsx_export.py`) segue a descrição do
briefing e ainda está pendente de validação contra o arquivo Excel real da
empresa (ex.: `QC_195_ALUMÍNIO`) — só o layout de colunas deve mudar quando
esse arquivo for compartilhado.
