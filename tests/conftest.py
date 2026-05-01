import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import Database, init_db
from dependencies import get_db
from tools.config import TEST_DB_PATH

@pytest.fixture(autouse=True)
def override_get_db(tmp_path):
    db_path = tmp_path / TEST_DB_PATH
    test_db = Database(str(db_path), max_connections=5)

    async def _init():
        await init_db(test_db)

    import asyncio
    asyncio.run(_init())

    app.dependency_overrides[get_db] = lambda: test_db

    yield test_db

    async def _close():
        await test_db.close_all()
    asyncio.run(_close())
    app.dependency_overrides = {}

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c