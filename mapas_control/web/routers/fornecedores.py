from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Query
from starlette.requests import Request

from mapas_control.models import Cotacao, Fornecedor
from mapas_control.storage.repository import Repository
from mapas_control.web.deps import get_repo, templates
from mapas_control.web.helpers import marcar_em_cotacao_se_necessario, parse_float_ou_none

router = APIRouter()


def _contexto_aba(repo: Repository, mapa_id: str, expandir_fornecedor_id: str | None = None) -> dict:
    ids_cotando = set(repo.fornecedores_cotando_no_mapa(mapa_id))
    todos = repo.listar_fornecedores()
    itens = repo.listar_itens(mapa_id)
    cotacoes = repo.listar_cotacoes_do_mapa(mapa_id)

    totais: dict[str, float] = {}
    cotacoes_por_fornecedor: dict[str, dict[str, Cotacao]] = {}
    for c in cotacoes:
        totais[c.fornecedor_id] = totais.get(c.fornecedor_id, 0.0) + c.total
        cotacoes_por_fornecedor.setdefault(c.fornecedor_id, {})[c.item_id] = c

    cotando = [f for f in todos if f.id in ids_cotando]
    disponiveis = [f for f in todos if f.id not in ids_cotando]

    # Fornecedor recém-criado ou escolhido no select ainda não tem cotação
    # nenhuma neste mapa — mostra ele mesmo assim, com o editor vazio.
    if expandir_fornecedor_id and expandir_fornecedor_id not in ids_cotando:
        extra = repo.buscar_fornecedor(expandir_fornecedor_id)
        if extra is not None:
            cotando = [extra] + cotando
            disponiveis = [f for f in disponiveis if f.id != expandir_fornecedor_id]

    return {
        "mapa_id": mapa_id,
        "itens": itens,
        "cotando": cotando,
        "disponiveis": disponiveis,
        "totais": totais,
        "cotacoes_por_fornecedor": cotacoes_por_fornecedor,
        "expandir_fornecedor_id": expandir_fornecedor_id,
    }


def _fornecedor_do_form(
    fornecedor_id: str | None, nome: str, contato: str, telefone: str, email: str,
    endereco: str, cidade: str, cnpj: str, inscricao_estadual: str, socio: str,
) -> Fornecedor:
    kwargs = dict(
        nome=nome.strip(),
        contato=contato.strip() or None,
        telefone=telefone.strip() or None,
        email=email.strip() or None,
        endereco=endereco.strip() or None,
        cidade=cidade.strip() or None,
        cnpj=cnpj.strip() or None,
        inscricao_estadual=inscricao_estadual.strip() or None,
        socio=socio.strip() or None,
    )
    if fornecedor_id is not None:
        kwargs["id"] = fornecedor_id
    return Fornecedor(**kwargs)


@router.get("/mapas/{mapa_id}/tabs/fornecedores")
def aba(mapa_id: str, request: Request, repo: Repository = Depends(get_repo)):
    return templates.TemplateResponse(request, "mapas/tab_fornecedores.html", _contexto_aba(repo, mapa_id))


@router.get("/mapas/{mapa_id}/fornecedores/cotacoes")
def selecionar_existente(
    mapa_id: str, request: Request, fornecedor_id: str = Query(...), repo: Repository = Depends(get_repo)
):
    """Fornecedor já cadastrado, escolhido no select pra cotar neste mapa —
    reaparece na lista com o editor de cotação vazio, expandido."""
    contexto = _contexto_aba(repo, mapa_id, expandir_fornecedor_id=fornecedor_id)
    return templates.TemplateResponse(request, "mapas/tab_fornecedores.html", contexto)


@router.post("/mapas/{mapa_id}/fornecedores")
def criar_fornecedor(
    mapa_id: str,
    request: Request,
    nome: str = Form(...),
    contato: str = Form(""),
    telefone: str = Form(""),
    email: str = Form(""),
    endereco: str = Form(""),
    cidade: str = Form(""),
    cnpj: str = Form(""),
    inscricao_estadual: str = Form(""),
    socio: str = Form(""),
    repo: Repository = Depends(get_repo),
):
    novo = repo.criar_fornecedor(
        _fornecedor_do_form(None, nome, contato, telefone, email, endereco, cidade, cnpj, inscricao_estadual, socio)
    )
    contexto = _contexto_aba(repo, mapa_id, expandir_fornecedor_id=novo.id)
    return templates.TemplateResponse(request, "mapas/tab_fornecedores.html", contexto)


@router.post("/mapas/{mapa_id}/fornecedores/{fornecedor_id}/cotacoes")
async def salvar_cotacoes(mapa_id: str, fornecedor_id: str, request: Request, repo: Repository = Depends(get_repo)):
    form = await request.form()
    for item in repo.listar_itens(mapa_id):
        preco = parse_float_ou_none(form.get(f"preco_unitario_{item.id}"))
        quantidade = parse_float_ou_none(form.get(f"quantidade_{item.id}"))
        if preco is not None and quantidade is not None:
            repo.lancar_cotacao(
                Cotacao(item_id=item.id, fornecedor_id=fornecedor_id, quantidade=quantidade, preco_unitario=preco)
            )

    mapa = repo.buscar_mapa(mapa_id)
    if mapa is not None:
        marcar_em_cotacao_se_necessario(repo, mapa)

    contexto = _contexto_aba(repo, mapa_id, expandir_fornecedor_id=fornecedor_id)
    return templates.TemplateResponse(request, "mapas/tab_fornecedores.html", contexto)


@router.get("/mapas/{mapa_id}/fornecedores/{fornecedor_id}/editar")
def editar_form(mapa_id: str, fornecedor_id: str, request: Request, repo: Repository = Depends(get_repo)):
    fornecedor = repo.buscar_fornecedor(fornecedor_id)
    return templates.TemplateResponse(
        request, "mapas/fornecedor_editar_form.html", {"mapa_id": mapa_id, "fornecedor": fornecedor}
    )


@router.post("/mapas/{mapa_id}/fornecedores/{fornecedor_id}/editar")
def editar_salvar(
    mapa_id: str,
    fornecedor_id: str,
    request: Request,
    nome: str = Form(...),
    contato: str = Form(""),
    telefone: str = Form(""),
    email: str = Form(""),
    endereco: str = Form(""),
    cidade: str = Form(""),
    cnpj: str = Form(""),
    inscricao_estadual: str = Form(""),
    socio: str = Form(""),
    repo: Repository = Depends(get_repo),
):
    repo.atualizar_fornecedor(
        _fornecedor_do_form(
            fornecedor_id, nome, contato, telefone, email, endereco, cidade, cnpj, inscricao_estadual, socio
        )
    )
    contexto = _contexto_aba(repo, mapa_id)
    return templates.TemplateResponse(request, "mapas/tab_fornecedores.html", contexto)
