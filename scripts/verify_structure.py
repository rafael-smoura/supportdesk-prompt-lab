"""Checks essential project files and JSON samples without external packages."""
import compileall
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    'README.md', '.env.example', '.gitignore', 'requirements.txt',
    'PROMPT_ENGINEERING_NOTES.md', 'run.py', 'main.py',
    'Dockerfile', 'docker-compose.yml',
    '.github/workflows/ci.yml',
    'docs/API.md', 'docs/ARQUITETURA.md',
    'docs/RESULTADO_DO_EXPERIMENTO.md',
    'frontend/index.html', 'frontend/app.js', 'frontend/style.css',
    'backend/api/routes.py', 'backend/services/generation.py',
    'backend/services/comparison.py', 'backend/services/prompts.py',
    'backend/providers/http.py',
    'tests/test_api.py', 'tests/test_prompts_and_providers.py',
]


def main():
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            raise SystemExit(f'ERRO: arquivo obrigatório ausente: {relative}')

    if (ROOT / '.git').is_dir():
        result = subprocess.run(['git', 'ls-files', '--error-unmatch', '.env'],
                                cwd=ROOT, capture_output=True)
        if result.returncode == 0:
            raise SystemExit('ERRO: .env não pode ser versionado')

    profiles = json.loads((ROOT / 'data/profiles.json').read_text(encoding='utf-8'))
    if not 3 <= len(profiles) <= 5:
        raise SystemExit('ERRO: o edital exige 3 a 5 perfis JSON')
    for profile in profiles:
        if not {'id', 'name', 'technical_level', 'communication_style', 'channel'} <= profile.keys():
            raise SystemExit(f'ERRO: perfil incompleto: {profile}')
        if profile['technical_level'] not in {'leigo', 'intermediário', 'avançado'}:
            raise SystemExit('ERRO: nível técnico inválido')
        if profile['communication_style'] not in {'direto', 'detalhado', 'didático'}:
            raise SystemExit('ERRO: estilo inválido')
        if profile['channel'] not in {'chat', 'e-mail', 'telefone'}:
            raise SystemExit('ERRO: canal inválido')

    json.loads((ROOT / 'data/tickets.json').read_text(encoding='utf-8'))
    samples = list((ROOT / 'samples').glob('*.json'))
    if not samples:
        raise SystemExit('ERRO: faltam exemplos JSON em samples/')
    for sample in samples:
        json.loads(sample.read_text(encoding='utf-8'))

    for subfolder in ('backend', 'tests'):
        if not compileall.compile_dir(str(ROOT / subfolder), quiet=1):
            raise SystemExit(f'ERRO: sintaxe Python inválida em {subfolder}')
    for filename in ('main.py', 'run.py'):
        if not compileall.compile_file(str(ROOT / filename), quiet=1):
            raise SystemExit(f'ERRO: sintaxe Python inválida em {filename}')

    print(f'OK: {len(REQUIRED_FILES)} arquivos essenciais, {len(profiles)} perfis, {len(samples)} amostras JSON.')
    print('Execute também python -m pytest -q e python scripts/preflight.py --strict.')


if __name__ == '__main__':
    main()
