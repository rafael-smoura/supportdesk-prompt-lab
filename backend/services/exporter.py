"""Exporta JSON de forma atômica para não deixar arquivos truncados."""
import json
import os
import tempfile
from pathlib import Path
from flask import current_app


def export_json(kind, identifier, payload):
    directory = Path(current_app.config["EXPORT_DIR"])
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{kind}_{identifier}.json"
    # O temporário fica no mesmo volume que o destino para permitir replace atômico.
    fd, temporary = tempfile.mkstemp(prefix=".tmp_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return target
