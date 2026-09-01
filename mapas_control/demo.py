"""Demo end-to-end do protótipo: monta uma obra/mapa de exemplo, lança
cotações de 3 fornecedores e gera os arquivos de saída (XLSX + 2 PDFs).

Rodar: python -m mapas_control.demo
"""

from __future__ import annotations

from pathlib import Path

from mapas_control.models import Cotacao, Fornecedor, Item, Mapa, Obra
from mapas_control.services import exportacao
from mapas_control.services.mapa_service import fechar_mapa
from mapas_control.services.regras import FornecedoresInsuficientesError, alertar_possiveis_duplicados
from mapas_control.storage.db import conectar, criar_schema
from mapas_control.storage.repository import Repository

SAIDA = Path(__file__).resolve().parent.parent / "output"


def main() -> None:
    conn = conectar(":memory:")
    criar_schema(conn)
    repo = Repository(conn)

    obra = repo.criar_obra(Obra(nome="Residencial Alfa"))
    mapa = repo.criar_mapa(Mapa(obra_id=obra.id, nome="Esquadrias de Alumínio"))

    itens = [
        repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Janela de correr 2 folhas 1,20x1,00", unidade="unid", quantidade_referencia=12)),
        repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL002", descricao="Porta de alumínio de abrir 0,90x2,10", unidade="unid", quantidade_referencia=6)),
        repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL003", descricao="Guarda-corpo em alumínio com vidro", unidade="m", quantidade_referencia=25)),
        repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL004", descricao="Fachada estrutural em alumínio", unidade="m²", quantidade_referencia=40)),
    ]

    print("Alertas de possível duplicidade:", alertar_possiveis_duplicados(itens) or "nenhum")

    fornecedor_a = repo.criar_fornecedor(Fornecedor(nome="Esquadrias Silva"))
    fornecedor_b = repo.criar_fornecedor(Fornecedor(nome="Alumitech"))
    fornecedor_c = repo.criar_fornecedor(Fornecedor(nome="Vidroforte Alumínio"))

    # Fornecedor A cota tudo.
    repo.lancar_cotacao(Cotacao(item_id=itens[0].id, fornecedor_id=fornecedor_a.id, quantidade=12, preco_unitario=850.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[1].id, fornecedor_id=fornecedor_a.id, quantidade=6, preco_unitario=1200.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[2].id, fornecedor_id=fornecedor_a.id, quantidade=25, preco_unitario=310.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[3].id, fornecedor_id=fornecedor_a.id, quantidade=40, preco_unitario=980.00))

    # Fornecedor B não cotou o item AL004 (não orçado -> ausência de linha).
    repo.lancar_cotacao(Cotacao(item_id=itens[0].id, fornecedor_id=fornecedor_b.id, quantidade=12, preco_unitario=799.90))
    repo.lancar_cotacao(Cotacao(item_id=itens[1].id, fornecedor_id=fornecedor_b.id, quantidade=6, preco_unitario=1150.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[2].id, fornecedor_id=fornecedor_b.id, quantidade=26, preco_unitario=295.00))  # qtd diverge da referência - esperado

    # Fornecedor C cota tudo, com preço mais alto em alguns itens.
    repo.lancar_cotacao(Cotacao(item_id=itens[0].id, fornecedor_id=fornecedor_c.id, quantidade=12, preco_unitario=910.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[1].id, fornecedor_id=fornecedor_c.id, quantidade=6, preco_unitario=1180.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[2].id, fornecedor_id=fornecedor_c.id, quantidade=25, preco_unitario=305.00))
    repo.lancar_cotacao(Cotacao(item_id=itens[3].id, fornecedor_id=fornecedor_c.id, quantidade=40, preco_unitario=960.00))

    SAIDA.mkdir(exist_ok=True)

    exportacao.exportar_xlsx_comparacao(repo, mapa.id, str(SAIDA / "mapa_comparacao.xlsx"))
    exportacao.exportar_pdf_comparacao(repo, mapa.id, str(SAIDA / "mapa_comparacao.pdf"))
    exportacao.exportar_pdf_solicitacao(repo, mapa.id, str(SAIDA / "mapa_solicitacao.pdf"))
    print(f"Gerado com 3 fornecedores cotando: {SAIDA}/mapa_comparacao.xlsx, mapa_comparacao.pdf, mapa_solicitacao.pdf")

    fechar_mapa(repo, mapa.id)
    print(f"Mapa fechado com sucesso (status = {repo.buscar_mapa(mapa.id).status.value}).")

    # Demonstra o bloqueio: um segundo mapa com só 2 fornecedores não pode ser exportado nem fechado.
    mapa2 = repo.criar_mapa(Mapa(obra_id=obra.id, nome="Guarda-corpo (exemplo com só 2 fornecedores)"))
    item2 = repo.adicionar_item(Item(mapa_id=mapa2.id, codigo="GC01", descricao="Guarda-corpo em vidro temperado", unidade="m", quantidade_referencia=10))
    repo.lancar_cotacao(Cotacao(item_id=item2.id, fornecedor_id=fornecedor_a.id, quantidade=10, preco_unitario=400.00))
    repo.lancar_cotacao(Cotacao(item_id=item2.id, fornecedor_id=fornecedor_b.id, quantidade=10, preco_unitario=380.00))
    try:
        exportacao.exportar_xlsx_comparacao(repo, mapa2.id, str(SAIDA / "nao_deve_existir.xlsx"))
    except FornecedoresInsuficientesError as exc:
        print(f"Bloqueio funcionando como esperado: {exc}")


if __name__ == "__main__":
    main()
