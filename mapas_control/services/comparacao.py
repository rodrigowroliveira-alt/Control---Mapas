"""Monta a comparação lado a lado: itens x fornecedores, subtotal, melhor valor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mapas_control.models import Cotacao, Fornecedor, Item, Mapa
from mapas_control.storage.repository import Repository


@dataclass
class LinhaComparacao:
    item: Item
    cotacoes_por_fornecedor: dict[str, Optional[Cotacao]]
    melhor_fornecedor_id: Optional[str] = None
    melhor_total: Optional[float] = None


@dataclass
class Comparacao:
    mapa: Mapa
    fornecedores: list[Fornecedor]
    linhas: list[LinhaComparacao] = field(default_factory=list)
    subtotal_por_fornecedor: dict[str, float] = field(default_factory=dict)


def montar_comparacao(repo: Repository, mapa_id: str) -> Comparacao:
    mapa = repo.buscar_mapa(mapa_id)
    if mapa is None:
        raise ValueError(f"Mapa '{mapa_id}' não encontrado.")

    itens = repo.listar_itens(mapa_id)
    cotacoes = repo.listar_cotacoes_do_mapa(mapa_id)

    fornecedores_por_id = {f.id: f for f in repo.listar_fornecedores()}
    ids_fornecedores_no_mapa = {c.fornecedor_id for c in cotacoes}
    fornecedores = sorted(
        (fornecedores_por_id[fid] for fid in ids_fornecedores_no_mapa if fid in fornecedores_por_id),
        key=lambda f: f.nome,
    )

    cotacoes_por_item: dict[str, dict[str, Cotacao]] = {}
    for c in cotacoes:
        cotacoes_por_item.setdefault(c.item_id, {})[c.fornecedor_id] = c

    comparacao = Comparacao(mapa=mapa, fornecedores=fornecedores)
    subtotal: dict[str, float] = {f.id: 0.0 for f in fornecedores}

    for item in itens:
        cotacoes_item = cotacoes_por_item.get(item.id, {})
        linha = LinhaComparacao(item=item, cotacoes_por_fornecedor=cotacoes_item)

        # Melhor valor = menor total entre quem cotou; ausência não conta como zero.
        for fornecedor_id, cotacao in cotacoes_item.items():
            subtotal[fornecedor_id] = subtotal.get(fornecedor_id, 0.0) + cotacao.total
            if linha.melhor_total is None or cotacao.total < linha.melhor_total:
                linha.melhor_total = cotacao.total
                linha.melhor_fornecedor_id = fornecedor_id

        comparacao.linhas.append(linha)

    comparacao.subtotal_por_fornecedor = subtotal
    return comparacao
