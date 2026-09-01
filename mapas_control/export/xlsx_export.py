"""Exportação XLS do mapa de comparação.

Layout de colunas validado contra o arquivo real da empresa
(Azo_QC_195_ALUMÍNIO_rev4.xlsx, aba "QC0003" — o `QC_195_ALUMÍNIO` citado
no briefing): Item / Código / Descrição / Unidade / Qtd. Referência,
depois um bloco Quant./Custo Unitário/Total por fornecedor, e por fim
Melhor Valor Unitário / Melhor Valor Total. Mesma ordem e nomes de coluna
do arquivo real — só os blocos fora do escopo do v1 (saldo orçamentário,
condições comerciais do vencedor, indexador INCC/verba meta) ficam de fora
por decisão explícita (ver conversa de 2026-09-01).

Regras aplicadas aqui (decisões do briefing, mantidas mesmo onde o arquivo
real da empresa faz diferente):
- Sem célula mesclada em nenhuma hipótese (inclusive pro cabeçalho) —
  fragiliza a planilha, é a causa raiz dos problemas do modelo antigo.
- "Não orçado" = célula vazia, nunca texto "NÃO ORÇADO" (o arquivo real
  usa texto mesclado nesse caso; decidiu-se não reproduzir isso).
- Total é fórmula visível (=quantidade×custo), nunca valor digitado.
- Melhor valor por item (fornecedor com menor total) é destacado em verde.
- Melhor Valor Unitário/Total: mesma lógica do arquivo real — menor custo
  unitário entre quem cotou (MIN, ignora quem não cotou) × quantidade de
  referência. Fica em branco se a quantidade de referência ainda não foi
  medida ou se ninguém cotou o item (não entra em cálculo, só fica
  pendente — regra já definida no briefing).
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from mapas_control.services.comparacao import Comparacao

COLUNAS_FIXAS = ["Item", "Código", "Descrição", "Unidade", "Qtd. Referência"]
COLUNAS_POR_FORNECEDOR = ["Quant.", "Custo Unitário", "Total"]
COLUNAS_FINAIS = ["Melhor Valor Unitário", "Melhor Valor Total"]

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


def _coluna_final(comparacao: Comparacao) -> int:
    return len(COLUNAS_FIXAS) + len(comparacao.fornecedores) * len(COLUNAS_POR_FORNECEDOR) + 1


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

    for i, titulo in enumerate(COLUNAS_FINAIS):
        celula = ws.cell(row=_LINHA_CABECALHO_1, column=col + i, value=titulo)
        celula.font = _FONTE_CABECALHO
        celula.fill = _PREENCHIMENTO_CABECALHO
        celula.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.cell(row=_LINHA_CABECALHO_2, column=col + i).fill = _PREENCHIMENTO_CABECALHO


def _escrever_itens(ws: Worksheet, comparacao: Comparacao) -> int:
    linha = _PRIMEIRA_LINHA_ITEM
    for numero, linha_comp in enumerate(comparacao.linhas, start=1):
        item = linha_comp.item
        ws.cell(row=linha, column=1, value=numero)
        ws.cell(row=linha, column=2, value=item.codigo)
        ws.cell(row=linha, column=3, value=item.descricao)
        ws.cell(row=linha, column=4, value=item.unidade)
        ws.cell(row=linha, column=5, value=item.quantidade_referencia)

        col = len(COLUNAS_FIXAS) + 1
        colunas_custo_unitario: list[str] = []
        for fornecedor in comparacao.fornecedores:
            cotacao = linha_comp.cotacoes_por_fornecedor.get(fornecedor.id)
            col_qtd, col_custo, col_total = col, col + 1, col + 2
            colunas_custo_unitario.append(get_column_letter(col_custo))
            if cotacao is not None:
                ws.cell(row=linha, column=col_qtd, value=cotacao.quantidade)
                ws.cell(row=linha, column=col_custo, value=cotacao.preco_unitario)
                letra_qtd = get_column_letter(col_qtd)
                letra_custo = get_column_letter(col_custo)
                celula_total = ws.cell(row=linha, column=col_total, value=f"={letra_qtd}{linha}*{letra_custo}{linha}")
                celula_total.number_format = "#,##0.00"
                if fornecedor.id == linha_comp.melhor_fornecedor_id:
                    for c in (col_qtd, col_custo, col_total):
                        ws.cell(row=linha, column=c).fill = _PREENCHIMENTO_MELHOR_VALOR
            # cotacao is None => "não orçado": célula vazia, sem texto e sem mesclagem.
            col += len(COLUNAS_POR_FORNECEDOR)

        _escrever_melhor_valor(ws, linha, col, item, linha_comp, colunas_custo_unitario)
        linha += 1
    return linha - 1


def _escrever_melhor_valor(ws, linha, col, item, linha_comp, colunas_custo_unitario) -> None:
    col_unit, col_total = col, col + 1
    if linha_comp.melhor_fornecedor_id is None:
        return  # ninguém cotou este item — fica pendente, sem entrar em cálculo.

    letra_unit = get_column_letter(col_unit)
    referencias = ",".join(f"{c}{linha}" for c in colunas_custo_unitario)
    ws.cell(row=linha, column=col_unit, value=f"=MIN({referencias})").number_format = "#,##0.00"

    if item.quantidade_referencia is not None:
        letra_qtd_ref = get_column_letter(5)
        celula = ws.cell(row=linha, column=col_total, value=f"={letra_unit}{linha}*{letra_qtd_ref}{linha}")
        celula.number_format = "#,##0.00"
    # quantidade_referencia vazia => melhor valor total fica em branco, não entra em cálculo (regra do briefing).


def _escrever_subtotal(ws: Worksheet, comparacao: Comparacao, ultima_linha_item: int) -> None:
    linha_subtotal = ultima_linha_item + 1
    ws.cell(row=linha_subtotal, column=3, value="Subtotal").font = _FONTE_CABECALHO

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
    larguras_fixas = [7, 12, 42, 10, 14]
    for i, largura in enumerate(larguras_fixas, start=1):
        ws.column_dimensions[get_column_letter(i)].width = largura

    col = len(COLUNAS_FIXAS) + 1
    for _ in comparacao.fornecedores:
        for i in range(len(COLUNAS_POR_FORNECEDOR)):
            ws.column_dimensions[get_column_letter(col + i)].width = 14
        col += len(COLUNAS_POR_FORNECEDOR)

    for i in range(len(COLUNAS_FINAIS)):
        ws.column_dimensions[get_column_letter(col + i)].width = 16


def salvar_xlsx_comparacao(comparacao: Comparacao, caminho: str) -> None:
    gerar_xlsx_comparacao(comparacao).save(caminho)
