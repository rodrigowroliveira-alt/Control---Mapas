"""Regras de negócio que não são só constraint de banco.

MIN_FORNECEDORES_MAPA = 3: decisão do usuário (2026-09-01) — atualiza o v1 do
briefing, que previa 2 como critério de aceite. Vale tanto para exportar o
PDF/XLS de comparação final quanto para fechar o mapa (status = fechado).
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from mapas_control.models import Item

MIN_FORNECEDORES_MAPA = 3

# Acima disso, duas descrições são "parecidas o suficiente" pra alertar.
_LIMIAR_SIMILARIDADE_DESCRICAO = 0.85


class FornecedoresInsuficientesError(ValueError):
    def __init__(self, quantidade_atual: int):
        self.quantidade_atual = quantidade_atual
        super().__init__(
            f"O mapa tem apenas {quantidade_atual} fornecedor(es) cotando. "
            f"São necessários no mínimo {MIN_FORNECEDORES_MAPA} para gerar a "
            "comparação final ou fechar o mapa."
        )


def garantir_minimo_fornecedores(fornecedores_cotando: list[str]) -> None:
    if len(fornecedores_cotando) < MIN_FORNECEDORES_MAPA:
        raise FornecedoresInsuficientesError(len(fornecedores_cotando))


@dataclass
class AlertaDuplicidade:
    item_a: Item
    item_b: Item
    similaridade: float


def alertar_possiveis_duplicados(itens: list[Item]) -> list[AlertaDuplicidade]:
    """Não bloqueia — só sinaliza pares com descrição muito parecida e mesma
    quantidade de referência, pra revisão manual (problema real do modelo antigo)."""
    alertas: list[AlertaDuplicidade] = []
    for i, item_a in enumerate(itens):
        for item_b in itens[i + 1 :]:
            if item_a.quantidade_referencia != item_b.quantidade_referencia:
                continue
            if item_a.quantidade_referencia is None:
                continue
            similaridade = SequenceMatcher(
                None, item_a.descricao.lower(), item_b.descricao.lower()
            ).ratio()
            if similaridade >= _LIMIAR_SIMILARIDADE_DESCRICAO:
                alertas.append(AlertaDuplicidade(item_a, item_b, similaridade))
    return alertas
