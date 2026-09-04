"""Popula o banco on-disk com o mesmo cenário de demo.py, pra abrir a app já
com dado de exemplo em vez de vazia. Idempotente — roda de novo sem duplicar.

Uso: python -m mapas_control.web.seed
"""

from __future__ import annotations

from mapas_control.models import Cotacao, Fornecedor, Item, Mapa, Obra
from mapas_control.storage.db import conectar, criar_schema
from mapas_control.storage.repository import Repository
from mapas_control.web.deps import DB_PATH
from mapas_control.web.helpers import marcar_em_cotacao_se_necessario


def seed_demo_data(repo: Repository) -> None:
    if repo.listar_obras():
        print("Já existem dados — seed pulado (idempotente).")
        return

    obra = repo.criar_obra(Obra(nome="Residencial Alfa"))

    # --- Mapa 1: Esquadrias de Alumínio — 3 fornecedores, liberado ---
    mapa1 = repo.criar_mapa(Mapa(obra_id=obra.id, nome="Esquadrias de Alumínio"))
    itens1 = [
        repo.adicionar_item(Item(mapa_id=mapa1.id, codigo="AL001", descricao="Janela de correr 2 folhas 1,20x1,00", unidade="unid", quantidade_referencia=12)),
        repo.adicionar_item(Item(mapa_id=mapa1.id, codigo="AL002", descricao="Porta de alumínio de abrir 0,90x2,10", unidade="unid", quantidade_referencia=6)),
        repo.adicionar_item(Item(mapa_id=mapa1.id, codigo="AL003", descricao="Guarda-corpo em alumínio com vidro", unidade="m", quantidade_referencia=25)),
        repo.adicionar_item(Item(mapa_id=mapa1.id, codigo="AL004", descricao="Fachada estrutural em alumínio", unidade="m²", quantidade_referencia=40)),
    ]
    fornecedor_a = repo.criar_fornecedor(
        Fornecedor(nome="Esquadrias Silva", contato="Wilton", telefone="5624-2023", email="wilton@esquadriassilva.com.br", cidade="São Paulo")
    )
    fornecedor_b = repo.criar_fornecedor(
        Fornecedor(nome="Alumitech", contato="Felipe", telefone="3799-0800", email="felipe@alumitech.com.br", cidade="Guarulhos", cnpj="12.345.678/0001-90")
    )
    fornecedor_c = repo.criar_fornecedor(
        Fornecedor(nome="Vidroforte Alumínio", contato="Carol", telefone="3648-3388", email="carol@vidroforte.com.br", cidade="São Paulo")
    )

    repo.lancar_cotacao(Cotacao(item_id=itens1[0].id, fornecedor_id=fornecedor_a.id, quantidade=12, preco_unitario=850.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[1].id, fornecedor_id=fornecedor_a.id, quantidade=6, preco_unitario=1200.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[2].id, fornecedor_id=fornecedor_a.id, quantidade=25, preco_unitario=310.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[3].id, fornecedor_id=fornecedor_a.id, quantidade=40, preco_unitario=980.00))

    # Fornecedor B não cotou AL004 (não orçado -> ausência de linha).
    repo.lancar_cotacao(Cotacao(item_id=itens1[0].id, fornecedor_id=fornecedor_b.id, quantidade=12, preco_unitario=799.90))
    repo.lancar_cotacao(Cotacao(item_id=itens1[1].id, fornecedor_id=fornecedor_b.id, quantidade=6, preco_unitario=1150.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[2].id, fornecedor_id=fornecedor_b.id, quantidade=26, preco_unitario=295.00))

    repo.lancar_cotacao(Cotacao(item_id=itens1[0].id, fornecedor_id=fornecedor_c.id, quantidade=12, preco_unitario=910.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[1].id, fornecedor_id=fornecedor_c.id, quantidade=6, preco_unitario=1180.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[2].id, fornecedor_id=fornecedor_c.id, quantidade=25, preco_unitario=305.00))
    repo.lancar_cotacao(Cotacao(item_id=itens1[3].id, fornecedor_id=fornecedor_c.id, quantidade=40, preco_unitario=960.00))

    marcar_em_cotacao_se_necessario(repo, mapa1)

    # --- Mapa 2: Guarda-corpo — só 2 fornecedores, bloqueado ---
    mapa2 = repo.criar_mapa(Mapa(obra_id=obra.id, nome="Guarda-corpo (exemplo com só 2 fornecedores)"))
    item2 = repo.adicionar_item(Item(mapa_id=mapa2.id, codigo="GC01", descricao="Guarda-corpo em vidro temperado", unidade="m", quantidade_referencia=10))
    repo.lancar_cotacao(Cotacao(item_id=item2.id, fornecedor_id=fornecedor_a.id, quantidade=10, preco_unitario=400.00))
    repo.lancar_cotacao(Cotacao(item_id=item2.id, fornecedor_id=fornecedor_b.id, quantidade=10, preco_unitario=380.00))
    marcar_em_cotacao_se_necessario(repo, mapa2)

    print(f"Seed concluído: obra '{obra.nome}' com 2 mapas em {DB_PATH}")


def main() -> None:
    conn = conectar(str(DB_PATH))
    criar_schema(conn)
    seed_demo_data(Repository(conn))
    conn.close()


if __name__ == "__main__":
    main()
