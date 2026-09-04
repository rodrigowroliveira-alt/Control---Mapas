from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from mapas_control.services.exportacao import (
    exportar_pdf_comparacao,
    exportar_pdf_solicitacao,
    exportar_xlsx_comparacao,
)
from mapas_control.services.regras import FornecedoresInsuficientesError
from mapas_control.storage.repository import Repository
from mapas_control.web.deps import get_repo

router = APIRouter()


def _nome_arquivo(mapa_id: str, repo: Repository, sufixo: str, extensao: str) -> str:
    mapa = repo.buscar_mapa(mapa_id)
    base = (mapa.nome if mapa else mapa_id).replace(" ", "_")
    return f"{base}_{sufixo}.{extensao}"


@router.get("/mapas/{mapa_id}/export/solicitacao-pdf")
def solicitacao_pdf(mapa_id: str, background_tasks: BackgroundTasks, repo: Repository = Depends(get_repo)):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    exportar_pdf_solicitacao(repo, mapa_id, tmp.name)
    background_tasks.add_task(os.unlink, tmp.name)
    return FileResponse(
        tmp.name,
        filename=_nome_arquivo(mapa_id, repo, "solicitacao", "pdf"),
        media_type="application/pdf",
        background=background_tasks,
    )


@router.get("/mapas/{mapa_id}/export/comparacao-pdf")
def comparacao_pdf(mapa_id: str, background_tasks: BackgroundTasks, repo: Repository = Depends(get_repo)):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    try:
        exportar_pdf_comparacao(repo, mapa_id, tmp.name)
    except FornecedoresInsuficientesError as exc:
        os.unlink(tmp.name)
        raise HTTPException(400, str(exc)) from exc
    background_tasks.add_task(os.unlink, tmp.name)
    return FileResponse(
        tmp.name,
        filename=_nome_arquivo(mapa_id, repo, "comparacao", "pdf"),
        media_type="application/pdf",
        background=background_tasks,
    )


@router.get("/mapas/{mapa_id}/export/comparacao-xlsx")
def comparacao_xlsx(mapa_id: str, background_tasks: BackgroundTasks, repo: Repository = Depends(get_repo)):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    tmp.close()
    try:
        exportar_xlsx_comparacao(repo, mapa_id, tmp.name)
    except FornecedoresInsuficientesError as exc:
        os.unlink(tmp.name)
        raise HTTPException(400, str(exc)) from exc
    background_tasks.add_task(os.unlink, tmp.name)
    return FileResponse(
        tmp.name,
        filename=_nome_arquivo(mapa_id, repo, "comparacao", "xlsx"),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=background_tasks,
    )
