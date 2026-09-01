"""Entidades do domínio de Mapas de Concorrência (ver mapas-codificados-briefing.md)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _novo_id() -> str:
    return str(uuid.uuid4())


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class StatusMapa(str, Enum):
    RASCUNHO = "rascunho"
    EM_COTACAO = "em_cotacao"
    FECHADO = "fechado"


@dataclass
class Obra:
    nome: str
    endereco: Optional[str] = None
    id: str = field(default_factory=_novo_id)
    criado_em: datetime = field(default_factory=_agora)


@dataclass
class Mapa:
    obra_id: str
    nome: str
    id: str = field(default_factory=_novo_id)
    status: StatusMapa = StatusMapa.RASCUNHO
    criado_em: datetime = field(default_factory=_agora)


@dataclass
class Item:
    mapa_id: str
    codigo: str
    descricao: str
    unidade: str
    quantidade_referencia: Optional[float] = None
    id: str = field(default_factory=_novo_id)


@dataclass
class Fornecedor:
    nome: str
    contato: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    id: str = field(default_factory=_novo_id)


@dataclass
class Cotacao:
    """Resposta de um Fornecedor para um Item. Ausência de registro = não orçado."""

    item_id: str
    fornecedor_id: str
    quantidade: float
    preco_unitario: float
    observacao: Optional[str] = None
    id: str = field(default_factory=_novo_id)
    lancado_em: datetime = field(default_factory=_agora)

    @property
    def total(self) -> float:
        # Sempre calculado — nunca um campo editável diretamente (regra de negócio).
        return round(self.quantidade * self.preco_unitario, 2)
