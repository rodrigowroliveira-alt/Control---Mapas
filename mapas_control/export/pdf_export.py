"""Exportação PDF: dois formatos, conforme o briefing.

- Comparação: todos os fornecedores lado a lado, com preço (uso interno).
- Solicitação: só itens + quantidade de referência, sem preço — para anexar
  no e-mail pedindo cotação a um fornecedor novo.
"""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from mapas_control.models import Item, Mapa
from mapas_control.services.comparacao import Comparacao

_ESTILOS = getSampleStyleSheet()
_ESTILO_TITULO = ParagraphStyle("TituloMapa", parent=_ESTILOS["Title"], fontSize=14, spaceAfter=4)
_ESTILO_SUBTITULO = ParagraphStyle("Subtitulo", parent=_ESTILOS["Normal"], fontSize=9, textColor=colors.grey)

_COR_CABECALHO = colors.HexColor("#D9D9D9")
_COR_MELHOR_VALOR = colors.HexColor("#C6EFCE")


def gerar_pdf_comparacao(comparacao: Comparacao, caminho: str) -> None:
    doc = SimpleDocTemplate(
        caminho,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    cabecalho1 = ["Código", "Descrição", "Unid.", "Qtd. Ref."]
    cabecalho2 = ["", "", "", ""]
    for fornecedor in comparacao.fornecedores:
        cabecalho1 += [fornecedor.nome, "", ""]
        cabecalho2 += ["Qtd.", "Custo Unitário", "Total"]

    dados = [cabecalho1, cabecalho2]
    celulas_melhor_valor: list[tuple[int, int]] = []  # (coluna, linha) para SPAN/BACKGROUND

    for idx, linha_comp in enumerate(comparacao.linhas):
        item = linha_comp.item
        linha_tabela = [item.codigo, item.descricao, item.unidade, _fmt(item.quantidade_referencia)]
        col_base = 4
        for fornecedor in comparacao.fornecedores:
            cotacao = linha_comp.cotacoes_por_fornecedor.get(fornecedor.id)
            if cotacao is None:
                linha_tabela += ["", "", ""]
            else:
                linha_tabela += [_fmt(cotacao.quantidade), _fmt(cotacao.preco_unitario), _fmt(cotacao.total)]
                if fornecedor.id == linha_comp.melhor_fornecedor_id:
                    linha_reportlab = idx + 2  # +2 pelas 2 linhas de cabeçalho
                    for c in range(col_base, col_base + 3):
                        celulas_melhor_valor.append((c, linha_reportlab))
            col_base += 3
        dados.append(linha_tabela)

    linha_subtotal = ["", "Subtotal", "", ""]
    for fornecedor in comparacao.fornecedores:
        linha_subtotal += ["", "", _fmt(comparacao.subtotal_por_fornecedor.get(fornecedor.id, 0.0))]
    dados.append(linha_subtotal)

    n_fixas = 4
    largura_fixa = [2.0 * cm, 6.5 * cm, 1.3 * cm, 2.0 * cm]
    largura_fornecedor = [1.8 * cm, 2.2 * cm, 2.0 * cm]
    larguras = largura_fixa + largura_fornecedor * len(comparacao.fornecedores)

    tabela = Table(dados, colWidths=larguras, repeatRows=2)

    estilo = [
        ("BACKGROUND", (0, 0), (-1, 1), _COR_CABECALHO),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (n_fixas, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.4, colors.grey),
        ("SPAN", (0, 0), (0, 1)),
        ("SPAN", (1, 0), (1, 1)),
        ("SPAN", (2, 0), (2, 1)),
        ("SPAN", (3, 0), (3, 1)),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]
    col = n_fixas
    for _ in comparacao.fornecedores:
        estilo.append(("SPAN", (col, 0), (col + 2, 0)))
        col += 3
    for c, r in celulas_melhor_valor:
        estilo.append(("BACKGROUND", (c, r), (c, r), _COR_MELHOR_VALOR))

    tabela.setStyle(TableStyle(estilo))

    elementos = [
        Paragraph(f"{comparacao.mapa.nome} — Mapa de Concorrência (Comparação)", _ESTILO_TITULO),
        Paragraph(
            f"{len(comparacao.fornecedores)} fornecedor(es) cotando · melhor valor por item destacado em verde",
            _ESTILO_SUBTITULO,
        ),
        Spacer(1, 0.4 * cm),
        tabela,
    ]
    doc.build(elementos)


def gerar_pdf_solicitacao(mapa: Mapa, itens: list[Item], caminho: str) -> None:
    doc = SimpleDocTemplate(caminho, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm)

    dados = [["Código", "Descrição", "Unidade", "Qtd. Referência"]]
    for item in itens:
        dados.append([item.codigo, item.descricao, item.unidade, _fmt(item.quantidade_referencia)])

    tabela = Table(dados, colWidths=[2.5 * cm, 10 * cm, 2.5 * cm, 3 * cm], repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _COR_CABECALHO),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ALIGN", (3, 1), (3, -1), "RIGHT"),
            ]
        )
    )

    elementos = [
        Paragraph(f"Solicitação de Cotação — {mapa.nome}", _ESTILO_TITULO),
        Paragraph("Favor retornar preço unitário para os itens abaixo.", _ESTILO_SUBTITULO),
        Spacer(1, 0.4 * cm),
        tabela,
    ]
    doc.build(elementos)


def _fmt(valor) -> str:
    if valor is None:
        return ""
    return f"{valor:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")
