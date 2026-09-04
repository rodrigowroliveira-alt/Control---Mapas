from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.requests import Request

from mapas_control.services.comparacao import montar_comparacao
from mapas_control.services.regras import MIN_FORNECEDORES_MAPA
from mapas_control.storage.repository import Repository
from mapas_control.web.deps import get_repo, templates

router = APIRouter()


@router.get("/mapas/{mapa_id}/tabs/comparacao")
def aba(mapa_id: str, request: Request, repo: Repository = Depends(get_repo)):
    comparacao = montar_comparacao(repo, mapa_id)
    qtd_fornecedores = len(comparacao.fornecedores)
    return templates.TemplateResponse(
        request,
        "mapas/tab_comparacao.html",
        {
            "mapa_id": mapa_id,
            "comparacao": comparacao,
            "qtd_fornecedores": qtd_fornecedores,
            "bloqueado": qtd_fornecedores < MIN_FORNECEDORES_MAPA,
            "faltam": max(0, MIN_FORNECEDORES_MAPA - qtd_fornecedores),
        },
    )
