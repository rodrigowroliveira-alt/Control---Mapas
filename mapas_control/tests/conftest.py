import pytest

from mapas_control.storage.db import conectar, criar_schema
from mapas_control.storage.repository import Repository


@pytest.fixture
def repo() -> Repository:
    conn = conectar(":memory:")
    criar_schema(conn)
    return Repository(conn)
