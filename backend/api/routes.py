"""Controladores HTTP: validação de entrada, status e serialização JSON."""
import hmac
from io import BytesIO
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from backend.repositories.generations import GenerationRepository, ComparisonRepository
from backend.services.catalog import read_catalog
from backend.services.comparison import ComparisonService
from backend.services.generation import GenerationService
from backend.services.exporter import export_json
from backend.providers.base import ProviderError

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.before_request
def require_access_token():
    if request.endpoint == "api.health":
        return None
    expected = current_app.config.get("APP_ACCESS_TOKEN", "")
    if expected and not hmac.compare_digest(request.headers.get("X-Access-Token", ""), expected):
        return jsonify({"error": "Token de acesso ausente ou inválido"}), 401
    return None


@api.after_request
def secure_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@api.errorhandler(RequestEntityTooLarge)
def payload_too_large(_):
    return jsonify({"error": "Requisição grande demais"}), 413


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.get("/meta")
def meta():
    return jsonify({
        "provider": current_app.config["AI_PROVIDER"],
        "model": current_app.config["AI_MODEL"],
        "is_demo": current_app.config["AI_PROVIDER"] == "demo",
        "versions": ["v1", "v2"],
        "content_types": ["diagnosis", "resolution", "questions", "flowchart"],
        "exports": "instance/history/",
    })


@api.get("/profiles")
def profiles():
    return jsonify(read_catalog("profiles.json"))


@api.get("/tickets")
def tickets():
    return jsonify(read_catalog("tickets.json"))


def _json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Envie um objeto JSON no corpo da requisição")
    return data


def _generate(payload):
    return GenerationService(current_app.config).generate(payload)


@api.post("/runs")
def new_run():
    try:
        record, cached = _generate(_json_body())
        return jsonify({"record": record.to_dict(), "cached": cached, "export": f"instance/history/generation_{record.id}.json"}), (200 if cached else 201)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), exc.status_code
    except Exception:
        current_app.logger.exception("Falha na geração")
        return jsonify({"error": "Falha interna ao gerar ou salvar conteúdo"}), 500


@api.post("/experiments")
def experiment():
    try:
        payload = _json_body()
        service = GenerationService(current_app.config)
        results = []
        for version in ("v1", "v2"):
            record, cached = service.generate({**payload, "prompt_version": version})
            results.append({"record": record.to_dict(), "cached": cached})
        return jsonify({"runs": results, "next_step": "Avaliar cada execução e registrar a comparação."}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), exc.status_code
    except Exception:
        current_app.logger.exception("Falha no experimento")
        return jsonify({"error": "Falha interna ao executar experimento"}), 500


@api.get("/runs")
def list_runs():
    return jsonify([run.to_dict() for run in GenerationRepository().recent()])


@api.get("/runs/<int:run_id>")
def get_run(run_id):
    run = GenerationRepository().by_id(run_id)
    return (jsonify(run.to_dict()), 200) if run else (jsonify({"error": "Execução não encontrada"}), 404)


@api.put("/runs/<int:run_id>/evaluation")
def evaluate(run_id):
    try:
        record = ComparisonService().evaluate(run_id, _json_body())
        return jsonify(record.to_dict())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception:
        current_app.logger.exception("Erro ao avaliar")
        return jsonify({"error": "Falha interna ao salvar avaliação"}), 500


@api.post("/comparisons")
def create_comparison():
    try:
        result = ComparisonService().compare(_json_body().get("generation_ids"))
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception:
        current_app.logger.exception("Erro ao comparar")
        return jsonify({"error": "Falha interna ao salvar comparação"}), 500


@api.get("/comparisons")
def list_comparisons():
    return jsonify([c.to_dict() for c in ComparisonRepository().recent()])


@api.get("/comparisons/<int:comparison_id>")
def get_comparison(comparison_id):
    try:
        return jsonify(ComparisonService().get(comparison_id))
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404


def _export(kind, id_, loader):
    try:
        data = loader(id_)
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    if data is None:
        return jsonify({"error": "Registro não encontrado"}), 404
    path = export_json(kind, id_, data)
    # Evita manter o arquivo aberto durante o download: no Windows, o bloqueio
    # impediria os.replace() ao atualizar uma comparação já exportada.
    content = BytesIO(path.read_bytes())
    return send_file(content, as_attachment=True, download_name=path.name,
                     mimetype="application/json")


@api.get("/runs/<int:run_id>/export")
def export_run(run_id):
    def lookup(identifier):
        result = GenerationRepository().by_id(identifier)
        return result.to_dict() if result else None
    return _export("generation", run_id, lookup)


@api.get("/comparisons/<int:comparison_id>/export")
def export_comparison(comparison_id):
    return _export("comparison", comparison_id, ComparisonService().get)
