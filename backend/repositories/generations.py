"""Consultas SQLAlchemy centralizadas (Repository Pattern)."""
from backend.extensions import db
from backend.models.entities import Generation, Comparison


class GenerationRepository:
    def cached(self, key):
        return db.session.query(Generation).filter_by(cache_key=key).first()

    def by_id(self, id_):
        return db.session.get(Generation, id_)

    def recent(self, limit=40):
        return db.session.query(Generation).order_by(Generation.id.desc()).limit(limit).all()

    def save(self, record):
        db.session.add(record)
        db.session.commit()
        return record


class ComparisonRepository:
    def by_pair(self, pair_key):
        return db.session.query(Comparison).filter_by(pair_key=pair_key).first()

    def by_id(self, id_):
        return db.session.get(Comparison, id_)

    def recent(self, limit=40):
        return db.session.query(Comparison).order_by(Comparison.id.desc()).limit(limit).all()

    def save(self, record):
        db.session.add(record)
        db.session.commit()
        return record
