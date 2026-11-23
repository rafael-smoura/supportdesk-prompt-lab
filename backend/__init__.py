"""Application Factory e composição das camadas."""
from pathlib import Path
from flask import Flask, send_from_directory
from backend.config import Config
from backend.extensions import db


def create_app(overrides=None):
    root = Path(__file__).resolve().parents[1]
    instance_dir = root / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    app = Flask(__name__, instance_path=str(instance_dir), static_folder=str(root / "frontend"), static_url_path="")
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    if app.config["APP_ENV"] == "production" and not app.config.get("APP_ACCESS_TOKEN"):
        raise RuntimeError("Configure APP_ACCESS_TOKEN antes de expor a aplicação em produção")
    db.init_app(app)
    from backend.models.entities import Generation, Comparison  # noqa: F401: registrar mapeamentos
    from backend.api.routes import api
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    with app.app_context():
        db.create_all()
    return app
