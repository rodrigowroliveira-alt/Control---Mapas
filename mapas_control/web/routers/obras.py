from __future__ import annotations

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from mapas_control.models import Obra
from mapas_control.storage.repository import Repository
from mapas_control.web.deps import get_repo, templates

router = APIRouter()


@router.get("/obras")
def listar(request: Request, repo: Repository = Depends(get_repo)):
    obras = repo.listar_obras()
    contagens = {o.id: len(repo.listar_mapas(o.id)) for o in obras}
    return templates.TemplateResponse(
        request, "obras/list.html", {"obras": obras, "contagens": contagens}
    )


@router.post("/obras")
def criar(nome: str = Form(...), endereco: str = Form(""), repo: Repository = Depends(get_repo)):
    repo.criar_obra(Obra(nome=nome.strip(), endereco=endereco.strip() or None))
    return RedirectResponse("/obras", status_code=303)
