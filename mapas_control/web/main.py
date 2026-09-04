"""Entrypoint da aplicação web do módulo Mapas de Concorrência.

Rodar com: uvicorn mapas_control.web.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from mapas_control.storage.db import conectar, criar_schema
from mapas_control.web.deps import DB_PATH
from mapas_control.web.routers import comparacao, exportacoes, fornecedores, itens, mapas, obras


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = conectar(str(DB_PATH))
    criar_schema(conn)
    conn.close()
    yield


app = FastAPI(title="Control — Mapas de Concorrência", lifespan=lifespan)
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)

app.include_router(obras.router)
app.include_router(mapas.router)
app.include_router(itens.router)
app.include_router(fornecedores.router)
app.include_router(comparacao.router)
app.include_router(exportacoes.router)


@app.get("/")
def raiz() -> RedirectResponse:
    return RedirectResponse("/obras")
