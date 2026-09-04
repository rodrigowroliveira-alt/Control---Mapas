"""Utilitários da camada web — nenhuma regra de negócio nova aqui."""

from __future__ import annotations

from typing import Optional

from mapas_control.models import Mapa, StatusMapa
from mapas_control.storage.repository import Repository


def marcar_em_cotacao_se_necessario(repo: Repository, mapa: Mapa) -> None:
    """Primeira cotação lançada num mapa ainda em rascunho -> em_cotacao.

    Usa só o método genérico já existente no repositório — não é uma regra
    de negócio nova, é uma transição de status que o backend já suporta."""
    if mapa.status == StatusMapa.RASCUNHO:
        repo.atualizar_status_mapa(mapa.id, StatusMapa.EM_COTACAO)


def parse_float_ou_none(valor: Optional[str]) -> Optional[float]:
    if valor is None or valor.strip() == "":
        return None
    return float(valor)
