"""Repositório: CRUD sobre o SQLite + as validações de gravação do briefing.

Regras aplicadas aqui (não apenas no banco), porque a mensagem de erro
precisa ser clara para quem está lançando dado, não um IntegrityError cru:
- código de item único dentro do mapa
- total da cotação nunca é gravado diretamente, é sempre calculado
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

from mapas_control.models import Cotacao, Fornecedor, Item, Mapa, Obra, StatusMapa


class CodigoDuplicadoError(ValueError):
    pass


class Repository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    # -- Obra ----------------------------------------------------------
    def criar_obra(self, obra: Obra) -> Obra:
        self._conn.execute(
            "INSERT INTO obra (id, nome, endereco, criado_em) VALUES (?, ?, ?, ?)",
            (obra.id, obra.nome, obra.endereco, obra.criado_em.isoformat()),
        )
        self._conn.commit()
        return obra

    # -- Mapa ------------------------------------------------------------
    def criar_mapa(self, mapa: Mapa) -> Mapa:
        self._conn.execute(
            "INSERT INTO mapa (id, obra_id, nome, status, criado_em) VALUES (?, ?, ?, ?, ?)",
            (mapa.id, mapa.obra_id, mapa.nome, mapa.status.value, mapa.criado_em.isoformat()),
        )
        self._conn.commit()
        return mapa

    def buscar_mapa(self, mapa_id: str) -> Optional[Mapa]:
        row = self._conn.execute("SELECT * FROM mapa WHERE id = ?", (mapa_id,)).fetchone()
        if row is None:
            return None
        return Mapa(
            id=row["id"],
            obra_id=row["obra_id"],
            nome=row["nome"],
            status=StatusMapa(row["status"]),
            criado_em=datetime.fromisoformat(row["criado_em"]),
        )

    def atualizar_status_mapa(self, mapa_id: str, status: StatusMapa) -> None:
        self._conn.execute("UPDATE mapa SET status = ? WHERE id = ?", (status.value, mapa_id))
        self._conn.commit()

    # -- Item --------------------------------------------------------------
    def adicionar_item(self, item: Item) -> Item:
        try:
            self._conn.execute(
                """INSERT INTO item (id, mapa_id, codigo, descricao, unidade, quantidade_referencia)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (item.id, item.mapa_id, item.codigo, item.descricao, item.unidade, item.quantidade_referencia),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc):
                raise CodigoDuplicadoError(
                    f"Já existe um item com o código '{item.codigo}' neste mapa. "
                    "Cada código deve ser único dentro do mapa."
                ) from exc
            raise
        return item

    def listar_itens(self, mapa_id: str) -> list[Item]:
        rows = self._conn.execute(
            "SELECT * FROM item WHERE mapa_id = ? ORDER BY codigo", (mapa_id,)
        ).fetchall()
        return [
            Item(
                id=r["id"],
                mapa_id=r["mapa_id"],
                codigo=r["codigo"],
                descricao=r["descricao"],
                unidade=r["unidade"],
                quantidade_referencia=r["quantidade_referencia"],
            )
            for r in rows
        ]

    # -- Fornecedor ----------------------------------------------------
    def criar_fornecedor(self, fornecedor: Fornecedor) -> Fornecedor:
        self._conn.execute(
            "INSERT INTO fornecedor (id, nome, contato, telefone, email) VALUES (?, ?, ?, ?, ?)",
            (fornecedor.id, fornecedor.nome, fornecedor.contato, fornecedor.telefone, fornecedor.email),
        )
        self._conn.commit()
        return fornecedor

    def listar_fornecedores(self) -> list[Fornecedor]:
        rows = self._conn.execute("SELECT * FROM fornecedor ORDER BY nome").fetchall()
        return [
            Fornecedor(id=r["id"], nome=r["nome"], contato=r["contato"], telefone=r["telefone"], email=r["email"])
            for r in rows
        ]

    # -- Cotação -----------------------------------------------------------
    def lancar_cotacao(self, cotacao: Cotacao) -> Cotacao:
        """Insere a cotação; se já existir uma para (item, fornecedor), atualiza."""
        self._conn.execute(
            """INSERT INTO cotacao (id, item_id, fornecedor_id, quantidade, preco_unitario, observacao, lancado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (item_id, fornecedor_id) DO UPDATE SET
                   quantidade = excluded.quantidade,
                   preco_unitario = excluded.preco_unitario,
                   observacao = excluded.observacao,
                   lancado_em = excluded.lancado_em""",
            (
                cotacao.id,
                cotacao.item_id,
                cotacao.fornecedor_id,
                cotacao.quantidade,
                cotacao.preco_unitario,
                cotacao.observacao,
                cotacao.lancado_em.isoformat(),
            ),
        )
        self._conn.commit()
        return cotacao

    def listar_cotacoes_do_mapa(self, mapa_id: str) -> list[Cotacao]:
        rows = self._conn.execute(
            """SELECT c.* FROM cotacao c
               JOIN item i ON i.id = c.item_id
               WHERE i.mapa_id = ?""",
            (mapa_id,),
        ).fetchall()
        return [
            Cotacao(
                id=r["id"],
                item_id=r["item_id"],
                fornecedor_id=r["fornecedor_id"],
                quantidade=r["quantidade"],
                preco_unitario=r["preco_unitario"],
                observacao=r["observacao"],
                lancado_em=datetime.fromisoformat(r["lancado_em"]),
            )
            for r in rows
        ]

    def fornecedores_cotando_no_mapa(self, mapa_id: str) -> list[str]:
        """IDs distintos de fornecedores que lançaram ao menos uma cotação neste mapa."""
        rows = self._conn.execute(
            """SELECT DISTINCT c.fornecedor_id FROM cotacao c
               JOIN item i ON i.id = c.item_id
               WHERE i.mapa_id = ?""",
            (mapa_id,),
        ).fetchall()
        return [r["fornecedor_id"] for r in rows]
