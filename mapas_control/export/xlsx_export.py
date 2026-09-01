"""Exportação XLS do mapa de comparação.

⚠️ ESTRUTURA PENDENTE DE VALIDAÇÃO: este layout segue a descrição do
mapas-codificados-briefing.md (estilo "Quadro de Concorrência" — item
codificado por linha, colunas de quantidade/preço/total repetidas por
fornecedor). Quando o arquivo Excel real (ex.: QC_195_ALUMÍNIO) for
compartilhado, os nomes/ordem das colunas abaixo (COLUNAS_FIXAS e
COLUNAS_POR_FORNECEDOR) devem ser ajustados para bater exatamente com ele
— é a única coisa que deve mudar, o resto (fórmulas, sem célula mesclada,
destaque do melhor valor) já reflete as regras de negócio decididas.

Regras aplicadas aqui:
- Sem célula mesclada em nenhuma hipótese (inclusive pro cabeçalho) —
  fragiliza a planilha, é a causa raiz dos problemas do modelo antigo.
- "Não orçado" = célula vazia, nunca texto tipo "NÃO ORÇADO".
- Total é fórmula visível (=quantidade×preço), nunca valor digitado.
- Melhor valor por item é destacado (preenchimento verde claro).
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from mapas_control.services.comparacao import Comparacao

COLUNAS_FIXAS = ["Código", "Descrição", "Unidade", "Qtd. Referência"]
COLUNAS_POR_FORNECEDOR = ["Quantidade", "Preço Unit.", "Total"]

_FONTE_CABECALHO = Font(bold=True)
_PREENCHIMENTO_CABECALHO = PatternFill("solid", fgColor="D9D9D9")
_PREENCHIMENTO_MELHOR_VALOR = PatternFill("solid", fgColor="C6EFCE")
_LINHA_CABECALHO_1 = 2
_LINHA_CABECALHO_2 = 3
_PRIMEIRA_LINHA_ITEM = 4


def gerar_xlsx_comparacao(comparacao: Comparacao) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Comparação"

    ws.cell(row=1, column=1, value=f"{comparacao.mapa.nome} — Mapa de Concorrência").font = Font(bold=True, size=13)

    _escrever_cabecalho(ws, comparacao)
    ultima_linha = _escrever_itens(ws, comparacao)
    _escrever_subtotal(ws, comparacao, ultima_linha)
    _ajustar_larguras(ws, comparacao)

    ws.freeze_panes = ws.cell(row=_PRIMEIRA_LINHA_ITEM, column=1)
    return wb


def _escrever_cabecalho(ws: Worksheet, comparacao: Comparacao) -> None:
    for col, titulo in enumerate(COLUNAS_FIXAS, start=1):
        celula = ws.cell(row=_LINHA_CABECALHO_1, column=col, value=titulo)
        celula.font = _FONTE_CABECALHO
        celula.fill = _PREENCHIMENTO_CABECALHO
        ws.cell(row=_LINHA_CABECALHO_2, column=col).fill = _PREENCHIMENTO_CABECALHO

    col = len(COLUNAS_FIXAS) + 1
    for fornecedor in comparacao.fornecedores:
        for i, subtitulo in enumerate(COLUNAS_POR_FORNECEDOR):
            c1 = ws.cell(row=_LINHA_CABECALHO_1, column=col + i, value=fornecedor.nome if i == 0 else None)
            c1.font = _FONTE_CABECALHO
            c1.fill = _PREENCHIMENTO_CABECALHO
            c2 = ws.cell(row=_LINHA_CABECALHO_2, column=col + i, value=subtitulo)
            c2.font = _FONTE_CABECALHO
            c2.fill = _PREENCHIMENTO_CABECALHO
            c2.alignment = Alignment(horizontal="center")
        col += len(COLUNAS_POR_FORNECEDOR)


def _escrever_itens(ws: Worksheet, comparacao: Comparacao) -> int:
    linha = _PRIMEIRA_LINHA_ITEM
    for linha_comp in comparacao.linhas:
        item = linha_comp.item
        ws.cell(row=linha, column=1, value=item.codigo)
        ws.cell(row=linha, column=2, value=item.descricao)
        ws.cell(row=linha, column=3, value=item.unidade)
        ws.cell(row=linha, column=4, value=item.quantidade_referencia)

        col = len(COLUNAS_FIXAS) + 1
        for fornecedor in comparacao.fornecedores:
            cotacao = linha_comp.cotacoes_por_fornecedor.get(fornecedor.id)
            col_qtd, col_preco, col_total = col, col + 1, col + 2
            if cotacao is not None:
                ws.cell(row=linha, column=col_qtd, value=cotacao.quantidade)
                ws.cell(row=linha, column=col_preco, value=cotacao.preco_unitario)
                letra_qtd = get_column_letter(col_qtd)
                letra_preco = get_column_letter(col_preco)
                celula_total = ws.cell(row=linha, column=col_total, value=f"={letra_qtd}{linha}*{letra_preco}{linha}")
                celula_total.number_format = "#,##0.00"
                if fornecedor.id == linha_comp.melhor_fornecedor_id:
                    for c in (col_qtd, col_preco, col_total):
                        ws.cell(row=linha, column=c).fill = _PREENCHIMENTO_MELHOR_VALOR
            # cotacao is None => "não orçado": célula vazia, sem texto e sem mesclagem.
            col += len(COLUNAS_POR_FORNECEDOR)
        linha += 1
    return linha - 1


def _escrever_subtotal(ws: Worksheet, comparacao: Comparacao, ultima_linha_item: int) -> None:
    linha_subtotal = ultima_linha_item + 1
    ws.cell(row=linha_subtotal, column=2, value="Subtotal").font = _FONTE_CABECALHO

    col = len(COLUNAS_FIXAS) + 1
    for _ in comparacao.fornecedores:
        col_total = col + 2
        letra_total = get_column_letter(col_total)
        celula = ws.cell(
            row=linha_subtotal,
            column=col_total,
            value=f"=SUM({letra_total}{_PRIMEIRA_LINHA_ITEM}:{letra_total}{ultima_linha_item})",
        )
        celula.font = _FONTE_CABECALHO
        celula.number_format = "#,##0.00"
        col += len(COLUNAS_POR_FORNECEDOR)


def _ajustar_larguras(ws: Worksheet, comparacao: Comparacao) -> None:
    larguras_fixas = [12, 42, 10, 14]
    for i, largura in enumerate(larguras_fixas, start=1):
        ws.column_dimensions[get_column_letter(i)].width = largura

    col = len(COLUNAS_FIXAS) + 1
    for _ in comparacao.fornecedores:
        for i in range(len(COLUNAS_POR_FORNECEDOR)):
            ws.column_dimensions[get_column_letter(col + i)].width = 14
        col += len(COLUNAS_POR_FORNECEDOR)


def salvar_xlsx_comparacao(comparacao: Comparacao, caminho: str) -> None:
    gerar_xlsx_comparacao(comparacao).save(caminho)
