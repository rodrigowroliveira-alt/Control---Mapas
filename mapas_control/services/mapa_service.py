"""Transições de status do mapa."""

from __future__ import annotations

from mapas_control.models import StatusMapa
from mapas_control.services.regras import garantir_minimo_fornecedores
from mapas_control.storage.repository import Repository


def fechar_mapa(repo: Repository, mapa_id: str) -> None:
    """Fecha o mapa (status -> fechado). Exige o mínimo de fornecedores cotando."""
    mapa = repo.buscar_mapa(mapa_id)
    if mapa is None:
        raise ValueError(f"Mapa '{mapa_id}' não encontrado.")

    fornecedores_cotando = repo.fornecedores_cotando_no_mapa(mapa_id)
    garantir_minimo_fornecedores(fornecedores_cotando)

    repo.atualizar_status_mapa(mapa_id, StatusMapa.FECHADO)
