"""Orquestra a exportação da comparação final.

Ponto único onde o gate de mínimo de fornecedores é aplicado, pra não
depender de cada chamador (CLI, futura API do Control etc.) lembrar de
checar antes de exportar.
"""

from __future__ import annotations

from mapas_control.export.pdf_export import gerar_pdf_comparacao, gerar_pdf_solicitacao
from mapas_control.export.xlsx_export import gerar_xlsx_comparacao
from mapas_control.services.comparacao import Comparacao, montar_comparacao
from mapas_control.services.regras import garantir_minimo_fornecedores
from mapas_control.storage.repository import Repository


def montar_comparacao_para_exportar(repo: Repository, mapa_id: str) -> Comparacao:
    fornecedores_cotando = repo.fornecedores_cotando_no_mapa(mapa_id)
    garantir_minimo_fornecedores(fornecedores_cotando)
    return montar_comparacao(repo, mapa_id)


def exportar_xlsx_comparacao(repo: Repository, mapa_id: str, caminho: str) -> None:
    comparacao = montar_comparacao_para_exportar(repo, mapa_id)
    gerar_xlsx_comparacao(comparacao).save(caminho)


def exportar_pdf_comparacao(repo: Repository, mapa_id: str, caminho: str) -> None:
    comparacao = montar_comparacao_para_exportar(repo, mapa_id)
    gerar_pdf_comparacao(comparacao, caminho)


def exportar_pdf_solicitacao(repo: Repository, mapa_id: str, caminho: str) -> None:
    """Sem gate: usado justamente pra pedir cotação a um fornecedor novo,
    antes de existir qualquer cotação lançada no mapa."""
    mapa = repo.buscar_mapa(mapa_id)
    if mapa is None:
        raise ValueError(f"Mapa '{mapa_id}' não encontrado.")
    itens = repo.listar_itens(mapa_id)
    gerar_pdf_solicitacao(mapa, itens, caminho)
