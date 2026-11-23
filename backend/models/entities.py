"""Modelos SQLAlchemy: execução individual e comparação auditável."""
from datetime import datetime, timezone
from backend.extensions import db


def utcnow():
    # Guardar ISO UTC como texto evita diferenças de timezone entre bancos.
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Generation(db.Model):
    __tablename__ = "generations"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.String(32), default=utcnow, nullable=False)
    customer_id = db.Column(db.String(60), nullable=False)
    profile = db.Column(db.JSON, nullable=False)
    ticket = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(24), nullable=False)
    prompt_version = db.Column(db.String(12), nullable=False)
    prompt_hash = db.Column(db.String(64), nullable=False)
    provider = db.Column(db.String(40), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    settings = db.Column(db.JSON, nullable=False)
    scenario_key = db.Column(db.String(64), nullable=False, index=True)
    cache_key = db.Column(db.String(64), nullable=False, unique=True, index=True)
    output = db.Column(db.JSON, nullable=False)
    evaluation = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "timestamp": self.created_at,
            "customer_id": self.customer_id, "profile": self.profile,
            "ticket": self.ticket, "content_type": self.content_type,
            "prompt_version": self.prompt_version, "prompt_hash": self.prompt_hash,
            "provider": self.provider, "model": self.model,
            "settings": self.settings, "scenario_key": self.scenario_key,
            "output": self.output, "evaluation": self.evaluation,
        }


class Comparison(db.Model):
    __tablename__ = "comparisons"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.String(32), default=utcnow, nullable=False)
    pair_key = db.Column(db.String(64), unique=True, nullable=False)
    scenario_key = db.Column(db.String(64), nullable=False)
    run_ids = db.Column(db.JSON, nullable=False)
    summary = db.Column(db.JSON, nullable=False)

    def to_dict(self, runs=None):
        data = {
            "id": self.id, "timestamp": self.created_at,
            "scenario_key": self.scenario_key, "generation_ids": self.run_ids,
            "summary": self.summary,
        }
        if runs is not None:
            data["results"] = [run.to_dict() for run in runs]
        return data
