import pytest

from mapas_control.models import Cotacao, Fornecedor, Item, Mapa, Obra, StatusMapa
from mapas_control.services.comparacao import montar_comparacao
from mapas_control.services.exportacao import exportar_xlsx_comparacao
from mapas_control.services.mapa_service import fechar_mapa
from mapas_control.services.regras import (
    FornecedoresInsuficientesError,
    alertar_possiveis_duplicados,
    garantir_minimo_fornecedores,
)
from mapas_control.storage.repository import CodigoDuplicadoError


def _mapa_basico(repo):
    obra = repo.criar_obra(Obra(nome="Obra Teste"))
    return repo.criar_mapa(Mapa(obra_id=obra.id, nome="Mapa Teste"))


def test_codigo_duplicado_e_bloqueado(repo):
    mapa = _mapa_basico(repo)
    repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Janela", unidade="unid"))
    with pytest.raises(CodigoDuplicadoError):
        repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Outra janela", unidade="unid"))


def test_codigo_igual_em_mapas_diferentes_e_permitido(repo):
    mapa1 = _mapa_basico(repo)
    mapa2 = repo.criar_mapa(Mapa(obra_id=mapa1.obra_id, nome="Outro Mapa"))
    repo.adicionar_item(Item(mapa_id=mapa1.id, codigo="AL001", descricao="Janela", unidade="unid"))
    # Não deve levantar: catálogo é por mapa, não global.
    repo.adicionar_item(Item(mapa_id=mapa2.id, codigo="AL001", descricao="Janela", unidade="unid"))


def test_total_da_cotacao_e_sempre_calculado():
    cotacao = Cotacao(item_id="x", fornecedor_id="y", quantidade=3, preco_unitario=10.5)
    assert cotacao.total == 31.5


def test_garantir_minimo_fornecedores_bloqueia_com_menos_de_3():
    with pytest.raises(FornecedoresInsuficientesError):
        garantir_minimo_fornecedores(["f1", "f2"])
    garantir_minimo_fornecedores(["f1", "f2", "f3"])  # não deve levantar


def test_exportar_xlsx_bloqueia_com_menos_de_3_fornecedores(repo, tmp_path):
    mapa = _mapa_basico(repo)
    item = repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Janela", unidade="unid", quantidade_referencia=10))
    f1 = repo.criar_fornecedor(Fornecedor(nome="Fornecedor 1"))
    f2 = repo.criar_fornecedor(Fornecedor(nome="Fornecedor 2"))
    repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=f1.id, quantidade=10, preco_unitario=5))
    repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=f2.id, quantidade=10, preco_unitario=6))

    with pytest.raises(FornecedoresInsuficientesError):
        exportar_xlsx_comparacao(repo, mapa.id, str(tmp_path / "saida.xlsx"))


def test_exportar_xlsx_funciona_com_3_fornecedores(repo, tmp_path):
    mapa = _mapa_basico(repo)
    item = repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Janela", unidade="unid", quantidade_referencia=10))
    for i in range(3):
        f = repo.criar_fornecedor(Fornecedor(nome=f"Fornecedor {i}"))
        repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=f.id, quantidade=10, preco_unitario=5 + i))

    caminho = tmp_path / "saida.xlsx"
    exportar_xlsx_comparacao(repo, mapa.id, str(caminho))
    assert caminho.exists()


def test_fechar_mapa_bloqueia_com_menos_de_3_fornecedores(repo):
    mapa = _mapa_basico(repo)
    item = repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Janela", unidade="unid"))
    f1 = repo.criar_fornecedor(Fornecedor(nome="Fornecedor 1"))
    f2 = repo.criar_fornecedor(Fornecedor(nome="Fornecedor 2"))
    repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=f1.id, quantidade=1, preco_unitario=1))
    repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=f2.id, quantidade=1, preco_unitario=1))

    with pytest.raises(FornecedoresInsuficientesError):
        fechar_mapa(repo, mapa.id)
    assert repo.buscar_mapa(mapa.id).status == StatusMapa.RASCUNHO


def test_melhor_valor_ignora_quem_nao_cotou(repo):
    mapa = _mapa_basico(repo)
    item = repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Janela", unidade="unid", quantidade_referencia=10))
    barato = repo.criar_fornecedor(Fornecedor(nome="Barato"))
    caro = repo.criar_fornecedor(Fornecedor(nome="Caro"))
    nao_cotou = repo.criar_fornecedor(Fornecedor(nome="Não Cotou"))

    repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=barato.id, quantidade=10, preco_unitario=5))
    repo.lancar_cotacao(Cotacao(item_id=item.id, fornecedor_id=caro.id, quantidade=10, preco_unitario=9))

    comparacao = montar_comparacao(repo, mapa.id)
    linha = comparacao.linhas[0]
    assert linha.melhor_fornecedor_id == barato.id
    assert linha.melhor_total == 50.0
    assert nao_cotou.id not in linha.cotacoes_por_fornecedor


def test_alerta_duplicidade_nao_bloqueia_so_sinaliza():
    itens = [
        Item(mapa_id="m", codigo="AL001", descricao="Janela de correr 2 folhas 1,20x1,00", unidade="unid", quantidade_referencia=12),
        Item(mapa_id="m", codigo="AL002", descricao="Janela de correr 2 folhas 1,20x1,00m", unidade="unid", quantidade_referencia=12),
    ]
    alertas = alertar_possiveis_duplicados(itens)
    assert len(alertas) == 1


def test_quantidade_referencia_pode_ficar_vazia(repo):
    mapa = _mapa_basico(repo)
    item = repo.adicionar_item(Item(mapa_id=mapa.id, codigo="AL001", descricao="Item ainda não medido", unidade="unid", quantidade_referencia=None))
    assert item.quantidade_referencia is None
