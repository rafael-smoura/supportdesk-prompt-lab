"""Comparação controlada: o único fator diferente deve ser o prompt."""
from backend.extensions import db
from backend.models.entities import Comparison
from backend.repositories.generations import GenerationRepository, ComparisonRepository
from backend.services.exporter import export_json
from backend.services.generation import digest
from backend.services.rubric import average, validate_rubric


class ComparisonService:
    def __init__(self, runs=None, comparisons=None):
        self.runs = runs or GenerationRepository()
        self.comparisons = comparisons or ComparisonRepository()

    def evaluate(self, run_id, rubric):
        record = self.runs.by_id(run_id)
        if record is None:
            raise LookupError("Execução não encontrada")
        record.evaluation = validate_rubric(rubric)
        db.session.commit()
        export_json("generation", record.id, record.to_dict())
        return record

    def compare(self, ids):
        if not isinstance(ids, list) or len(ids) != 2 or any(type(x) is not int for x in ids) or ids[0] == ids[1]:
            raise ValueError("Informe exatamente dois IDs de execução distintos")
        records = [self.runs.by_id(i) for i in ids]
        if any(record is None for record in records):
            raise LookupError("Execução não encontrada")
        a, b = records
        if a.scenario_key != b.scenario_key:
            raise ValueError("Compare o mesmo perfil, ticket, conteúdo, provedor, modelo e configurações")
        if {a.prompt_version, b.prompt_version} != {"v1", "v2"}:
            raise ValueError("É necessário comparar v1 com v2")
        if not a.evaluation or not b.evaluation:
            raise ValueError("Preencha as três notas e justificativas de ambas as versões")
        ordered = sorted(records, key=lambda r: r.prompt_version)
        first, second = ordered
        a_score, b_score = average(first.evaluation), average(second.evaluation)
        summary = {
            "v1_average": a_score, "v2_average": b_score,
            "delta_v2_minus_v1": round(b_score - a_score, 2),
            "higher_scored_version": "v1" if a_score > b_score else ("v2" if b_score > a_score else "tie"),
            "method": "Média simples de clareza, adequação e acionabilidade; avaliação humana.",
            "disclaimer": "Notas humanas não são teste estatístico nem prova automática de superioridade.",
        }
        pair_key = digest(sorted(ids))
        item = self.comparisons.by_pair(pair_key)
        if item:
            item.run_ids = [r.id for r in ordered]
            item.summary = summary
        else:
            item = Comparison(pair_key=pair_key, scenario_key=a.scenario_key,
                              run_ids=[r.id for r in ordered], summary=summary)
        self.comparisons.save(item)
        payload = item.to_dict(ordered)
        export_json("comparison", item.id, payload)
        return payload

    def get(self, id_):
        comparison = self.comparisons.by_id(id_)
        if comparison is None:
            raise LookupError("Comparação não encontrada")
        records = [self.runs.by_id(run_id) for run_id in comparison.run_ids]
        return comparison.to_dict(records)
