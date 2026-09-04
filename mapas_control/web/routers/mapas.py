from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, Response
from starlette.requests import Request

from mapas_control.models import Mapa
from mapas_control.services.comparacao import montar_comparacao
from mapas_control.services.mapa_service import fechar_mapa
from mapas_control.services.regras import MIN_FORNECEDORES_MAPA, FornecedoresInsuficientesError
from mapas_control.storage.repository import Repository
from mapas_control.web.deps import get_repo, templates

router = APIRouter()


@router.get("/obras/{obra_id}/mapas")
def listar(obra_id: str, request: Request, repo: Repository = Depends(get_repo)):
    obra = repo.buscar_obra(obra_id)
    if obra is None:
        raise HTTPException(404, "Obra não encontrada.")
    mapas = repo.listar_mapas(obra_id)
    fornecedores_por_mapa = {m.id: len(repo.fornecedores_cotando_no_mapa(m.id)) for m in mapas}
    return templates.TemplateResponse(
        request,
        "mapas/list.html",
        {"obra": obra, "mapas": mapas, "fornecedores_por_mapa": fornecedores_por_mapa},
    )


@router.post("/obras/{obra_id}/mapas")
def criar(obra_id: str, nome: str = Form(...), repo: Repository = Depends(get_repo)):
    repo.criar_mapa(Mapa(obra_id=obra_id, nome=nome.strip()))
    return RedirectResponse(f"/obras/{obra_id}/mapas", status_code=303)


@router.get("/mapas/{mapa_id}")
def detalhe(mapa_id: str, request: Request, repo: Repository = Depends(get_repo)):
    mapa = repo.buscar_mapa(mapa_id)
    if mapa is None:
        raise HTTPException(404, "Mapa não encontrado.")
    obra = repo.buscar_obra(mapa.obra_id)
    return templates.TemplateResponse(request, "mapas/detail.html", {"mapa": mapa, "obra": obra})


@router.post("/mapas/{mapa_id}/fechar")
def fechar(mapa_id: str, request: Request, repo: Repository = Depends(get_repo)):
    try:
        fechar_mapa(repo, mapa_id)
    except FornecedoresInsuficientesError:
        mapa = repo.buscar_mapa(mapa_id)
        comparacao = montar_comparacao(repo, mapa_id)
        qtd_fornecedores = len(comparacao.fornecedores)
        return templates.TemplateResponse(
            request,
            "mapas/tab_comparacao.html",
            {
                "mapa_id": mapa_id,
                "comparacao": comparacao,
                "qtd_fornecedores": qtd_fornecedores,
                "bloqueado": True,
                "faltam": MIN_FORNECEDORES_MAPA - qtd_fornecedores,
            },
        )
    return Response(status_code=200, headers={"HX-Redirect": f"/mapas/{mapa_id}"})
