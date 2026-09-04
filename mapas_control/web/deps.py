"""Dependências compartilhadas da app web: conexão por request e templates."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from fastapi.templating import Jinja2Templates

from mapas_control.storage.db import conectar
from mapas_control.storage.repository import Repository

DB_PATH = Path(__file__).resolve().parents[2] / "mapas_control.db"

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def get_repo() -> Iterator[Repository]:
    conn = conectar(str(DB_PATH))
    try:
        yield Repository(conn)
    finally:
        conn.close()
