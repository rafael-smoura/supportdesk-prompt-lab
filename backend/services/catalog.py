"""Catálogos pequenos e versionáveis, fora do código Python."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def read_catalog(name):
    if name not in {"profiles.json", "tickets.json"}:
        raise ValueError("Catálogo desconhecido")
    with (DATA_DIR / name).open(encoding="utf-8") as stream:
        return json.load(stream)


def find_profile(profile_id):
    return next((p for p in read_catalog("profiles.json") if p["id"] == profile_id), None)


def find_ticket(ticket_id):
    return next((t for t in read_catalog("tickets.json") if t["id"] == ticket_id), None)
