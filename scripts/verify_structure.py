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

# O .env local pode existir; o importante é que nunca esteja versionado.
import subprocess
if (ROOT / '.git').exists():
    tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', '.env'], cwd=ROOT,
                             capture_output=True, text=True).returncode == 0
    assert not tracked, 'O arquivo .env não pode ser versionado'
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
    if sample.name == 'rubric_input_TEMPLATE.json':
        continue
    if sample.name == 'comparacao_real_analisada.json':
        assert data.get('illustrative') is not True, 'Comparação real não pode ser ilustrativa'
        assert len(data.get('results', [])) == 2, 'Comparação real precisa de duas versões'
        assert {r.get('prompt_version') for r in data['results']} == {'v1', 'v2'}
        assert all(r.get('provider') != 'demo' and r.get('evaluation') for r in data['results'])
    else:
        assert data.get('illustrative') is True, f'Marque o exemplo {sample.name} como ilustrativo'

assert compileall.compile_dir(str(ROOT / 'backend'), quiet=1)
assert compileall.compile_dir(str(ROOT / 'tests'), quiet=1)
assert compileall.compile_file(str(ROOT / 'main.py'), quiet=1)
assert compileall.compile_file(str(ROOT / 'run.py'), quiet=1)
print(f'OK: {len(REQUIRED)} arquivos essenciais, {len(profiles)} perfis, exemplos JSON e sintaxe Python.')
print('Ainda é necessário executar pytest após instalar as dependências.')
