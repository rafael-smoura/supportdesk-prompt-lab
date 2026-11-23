"""Configurações centralizadas; segredos vêm exclusivamente do ambiente."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _float(name, default):
    value = float(os.getenv(name, default))
    if not 0 <= value <= 2:
        raise ValueError(f"{name} precisa estar entre 0 e 2")
    return value


def _int(name, default, low, high):
    value = int(os.getenv(name, default))
    if not low <= value <= high:
        raise ValueError(f"{name} deve estar entre {low} e {high}")
    return value


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///supportdesk.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_PROVIDER = os.getenv("AI_PROVIDER", "demo").lower()
    AI_MODEL = os.getenv("AI_MODEL", "demo-local")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_API_URL = os.getenv("AI_API_URL", "https://api.openai.com/v1/chat/completions")
    AI_TEMPERATURE = _float("AI_TEMPERATURE", "0.2")
    AI_MAX_TOKENS = _int("AI_MAX_TOKENS", "1300", 100, 8192)
    AI_TIMEOUT = _int("AI_TIMEOUT", "35", 5, 120)
    AI_JSON_MODE = os.getenv("AI_JSON_MODE", "true").strip().lower() in {"true", "1", "yes"}
    APP_ACCESS_TOKEN = os.getenv("APP_ACCESS_TOKEN", "")
    EXPORT_DIR = os.getenv("EXPORT_DIR", str(ROOT / "instance" / "history"))
    MAX_CONTENT_LENGTH = 15 * 1024
    JSON_SORT_KEYS = False
