"""Schema SQLite. Banco relacional simples é suficiente para o v1 (ver briefing)."""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS obra (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    endereco TEXT,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mapa (
    id TEXT PRIMARY KEY,
    obra_id TEXT NOT NULL REFERENCES obra(id),
    nome TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'rascunho'
        CHECK (status IN ('rascunho', 'em_cotacao', 'fechado')),
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item (
    id TEXT PRIMARY KEY,
    mapa_id TEXT NOT NULL REFERENCES mapa(id),
    codigo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    unidade TEXT NOT NULL,
    quantidade_referencia REAL,
    UNIQUE (mapa_id, codigo)
);

CREATE TABLE IF NOT EXISTS fornecedor (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    contato TEXT,
    telefone TEXT,
    email TEXT
);

-- Uma cotação por (item, fornecedor): relançar atualiza, não duplica.
CREATE TABLE IF NOT EXISTS cotacao (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL REFERENCES item(id),
    fornecedor_id TEXT NOT NULL REFERENCES fornecedor(id),
    quantidade REAL NOT NULL,
    preco_unitario REAL NOT NULL,
    total REAL GENERATED ALWAYS AS (ROUND(quantidade * preco_unitario, 2)) STORED,
    observacao TEXT,
    lancado_em TEXT NOT NULL,
    UNIQUE (item_id, fornecedor_id)
);
"""


def conectar(caminho: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
