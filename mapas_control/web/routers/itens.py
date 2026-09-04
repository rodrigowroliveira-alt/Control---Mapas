from __future__ import annotations

from fastapi import APIRouter, Depends, Form
from starlette.requests import Request

from mapas_control.models import Item
from mapas_control.storage.repository import CodigoDuplicadoError, Repository
from mapas_control.web.deps import get_repo, templates
from mapas_control.web.helpers import parse_float_ou_none

router = APIRouter()


@router.get("/mapas/{mapa_id}/tabs/itens")
def aba(mapa_id: str, request: Request, repo: Repository = Depends(get_repo)):
    itens = repo.listar_itens(mapa_id)
    return templates.TemplateResponse(
        request, "mapas/tab_itens.html", {"mapa_id": mapa_id, "itens": itens, "erro": None, "valores": None}
    )


@router.post("/mapas/{mapa_id}/itens")
def adicionar(
    mapa_id: str,
    request: Request,
    codigo: str = Form(...),
    descricao: str = Form(...),
    unidade: str = Form(...),
    quantidade_referencia: str = Form(""),
    repo: Repository = Depends(get_repo),
):
    erro = None
    valores = {
        "codigo": codigo,
        "descricao": descricao,
        "unidade": unidade,
        "quantidade_referencia": quantidade_referencia,
    }
    try:
        repo.adicionar_item(
            Item(
                mapa_id=mapa_id,
                codigo=codigo.strip(),
                descricao=descricao.strip(),
                unidade=unidade.strip(),
                quantidade_referencia=parse_float_ou_none(quantidade_referencia),
            )
        )
        valores = None
    except CodigoDuplicadoError as exc:
        erro = str(exc)

    itens = repo.listar_itens(mapa_id)
    return templates.TemplateResponse(
        request,
        "mapas/tab_itens.html",
        {"mapa_id": mapa_id, "itens": itens, "erro": erro, "valores": valores},
    )
