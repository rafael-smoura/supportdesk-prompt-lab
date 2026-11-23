from pathlib import Path
import pytest
from backend import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True, "APP_ENV": "testing",
        "AI_PROVIDER": "demo", "AI_MODEL": "demo-local",
        "AI_API_KEY": "", "APP_ACCESS_TOKEN": "",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'tests.db'}",
        "EXPORT_DIR": str(tmp_path / "history"),
        "AI_TEMPERATURE": 0.2, "AI_MAX_TOKENS": 1300,
        "AI_JSON_MODE": True, "AI_TIMEOUT": 15,
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def payload():
    return {"customer_id":"c1", "ticket":"Portal apresenta erro ao autenticar.",
            "content_type":"diagnosis", "prompt_version":"v1"}
