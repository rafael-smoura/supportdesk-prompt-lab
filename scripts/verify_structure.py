"""Pré-validação de estrutura com apenas a biblioteca padrão do Python.

Não substitui os testes de integração em Flask/SQLAlchemy.
"""
import compileall
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md', 'PROMPT_ENGINEERING_NOTES.md', '.env.example', '.env_example',
    'requirements.txt', 'requirements-dev.txt', 'Dockerfile', 'docker-compose.yml',
    'render.yaml', 'run.py', 'main.py',
    '.github/workflows/ci.yml', 'docs/PROXIMOS_PASSOS.md',
    'docs/GUIA_DE_PROXIMOS_PASSOS.pdf', 'docs/EXPERIMENTO_GUIADO.md',
    'frontend/index.html', 'frontend/app.js', 'frontend/style.css',
    'backend/api/routes.py', 'backend/services/generation.py',
    'backend/services/comparison.py', 'backend/services/prompts.py',
    'backend/providers/http.py', 'tests/test_api.py', 'tests/test_prompts_and_providers.py',
]
for relative in REQUIRED:
    assert (ROOT / relative).is_file(), f'Arquivo ausente: {relative}'

assert not (ROOT / '.env').exists(), 'Não distribua o arquivo .env'
profiles = json.loads((ROOT / 'data/profiles.json').read_text(encoding='utf-8'))
assert 3 <= len(profiles) <= 5
for profile in profiles:
    assert {'id', 'name', 'technical_level', 'communication_style', 'channel'} <= set(profile)
    assert profile['technical_level'] in {'leigo','intermediário','avançado'}
    assert profile['communication_style'] in {'direto','detalhado','didático'}
    assert profile['channel'] in {'chat','e-mail','telefone'}
assert json.loads((ROOT / 'data/tickets.json').read_text(encoding='utf-8'))
for sample in (ROOT / 'samples').glob('*.json'):
    data=json.loads(sample.read_text(encoding='utf-8'))
    if sample.name != 'rubric_input_TEMPLATE.json':
        assert data.get('illustrative') is True

assert compileall.compile_dir(str(ROOT / 'backend'), quiet=1)
assert compileall.compile_dir(str(ROOT / 'tests'), quiet=1)
assert compileall.compile_file(str(ROOT / 'main.py'), quiet=1)
assert compileall.compile_file(str(ROOT / 'run.py'), quiet=1)
print(f'OK: {len(REQUIRED)} arquivos essenciais, {len(profiles)} perfis, exemplos JSON e sintaxe Python.')
print('Ainda é necessário executar pytest após instalar as dependências.')
