"""Caso de uso: gerar conteúdo, deduplicar e registrar evidências."""
import hashlib
import json
from flask import current_app
from sqlalchemy.exc import IntegrityError
from backend.extensions import db
from backend.models.entities import Generation
from backend.providers.factory import create_provider
from backend.repositories.generations import GenerationRepository
from backend.services.exporter import export_json
from backend.services.prompts import build_messages
from backend.services.validators import validate_request, validate_output


def digest(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class GenerationService:
    def __init__(self, config, provider=None, repository=None):
        self.config = config
        self.provider = provider
        self.repository = repository or GenerationRepository()

    def generate(self, payload):
        profile, ticket, content_type, version = validate_request(payload)
        settings = {
            "api_url": self.config["AI_API_URL"] if self.config["AI_PROVIDER"] == "openai_compatible" else None,
            "temperature": float(self.config["AI_TEMPERATURE"]),
            "max_tokens": int(self.config["AI_MAX_TOKENS"]),
            "json_mode": bool(self.config["AI_JSON_MODE"]),
        }
        context = {
            "profile": profile, "ticket": ticket, "content_type": content_type,
            "provider": self.config["AI_PROVIDER"], "model": self.config["AI_MODEL"],
            "settings": settings,
        }
        scenario_key = digest(context)
        messages = build_messages(profile, ticket, content_type, version)
        prompt_hash = digest(messages)
        cache_key = digest({"scenario_key": scenario_key, "prompt_hash": prompt_hash})
        cached = self.repository.cached(cache_key)
        if cached:
            current_app.logger.info("cache_hit run_id=%s", cached.id)
            return cached, True
        provider = self.provider or create_provider(self.config)
        output = validate_output(content_type, provider.generate(messages, content_type))
        record = Generation(
            customer_id=profile["id"], profile=profile, ticket=ticket,
            content_type=content_type, prompt_version=version,
            prompt_hash=prompt_hash, provider=self.config["AI_PROVIDER"],
            model=self.config["AI_MODEL"], settings=settings,
            scenario_key=scenario_key, cache_key=cache_key, output=output,
        )
        try:
            self.repository.save(record)
        except IntegrityError:
            # Duas requisições concorrentes podem ter calculado a mesma chave.
            db.session.rollback()
            record = self.repository.cached(cache_key)
            if record is None:
                raise
            return record, True
        export_json("generation", record.id, record.to_dict())
        current_app.logger.info("generation_saved run_id=%s provider=%s", record.id, record.provider)
        return record, False
