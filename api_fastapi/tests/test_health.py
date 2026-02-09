import os
import importlib
from fastapi.testclient import TestClient


def test_health_ready():
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    from app import config as config_module
    importlib.reload(config_module)
    from app import db as db_module
    importlib.reload(db_module)
    from app import main as main_module
    importlib.reload(main_module)

    client = TestClient(main_module.app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}
