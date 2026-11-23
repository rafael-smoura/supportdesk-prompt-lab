"""Importa uma comparação exportada para um banco local vazio.

Não altera notas ou saídas. Em caso de IDs conflitantes, interrompe a importação.
"""
import argparse
import json
import sys
from pathlib import Path

# Executar como script funciona mesmo fora de um ambiente instalado como pacote.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import create_app
from backend.extensions import db
from backend.models.entities import Comparison, Generation
from backend.services.generation import digest


def import_comparison(filepath):
    data = json.loads(Path(filepath).read_text(encoding='utf-8'))
    records = data.get('results', [])
    if len(records) != 2 or {r.get('prompt_version') for r in records} != {'v1', 'v2'}:
        raise ValueError('O arquivo precisa conter uma comparação entre v1 e v2')
    if len({r.get('scenario_key') for r in records}) != 1:
        raise ValueError('As execuções não pertencem ao mesmo cenário')

    app = create_app()
    with app.app_context():
        for item in records:
            if db.session.get(Generation, item['id']):
                raise ValueError(f"Já existe uma execução com o ID {item['id']}; importação cancelada")
        if db.session.get(Comparison, data['id']):
            raise ValueError(f"Já existe comparação com o ID {data['id']}; importação cancelada")
        try:
            for item in records:
                db.session.add(Generation(
                    id=item['id'], created_at=item['timestamp'],
                    customer_id=item['customer_id'], profile=item['profile'],
                    ticket=item['ticket'], content_type=item['content_type'],
                    prompt_version=item['prompt_version'], prompt_hash=item['prompt_hash'],
                    provider=item['provider'], model=item['model'], settings=item['settings'],
                    scenario_key=item['scenario_key'],
                    cache_key=digest({'scenario_key': item['scenario_key'], 'prompt_hash': item['prompt_hash']}),
                    output=item['output'], evaluation=item['evaluation']
                ))
            db.session.add(Comparison(
                id=data['id'], created_at=data['timestamp'],
                pair_key=digest(sorted(data['generation_ids'])),
                scenario_key=data['scenario_key'], run_ids=data['generation_ids'],
                summary=data['summary']
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        print('Importação concluída. Abra o Histórico e revise as duas avaliações antes de entregar.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importar comparação real para SQLite local')
    parser.add_argument('path', help='Caminho do JSON exportado')
    import_comparison(parser.parse_args().path)
