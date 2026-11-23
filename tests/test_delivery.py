"""Checagens simples do pacote para evitar regressões de configuração."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_env_examples_match_and_do_not_expose_keys():
    example = (ROOT / '.env.example').read_text(encoding='utf-8')
    alias = (ROOT / '.env_example').read_text(encoding='utf-8')
    assert example == alias
    assert 'AI_PROVIDER=demo' in example
    assert 'AI_API_KEY=\n' in example
    assert 'APP_ACCESS_TOKEN=\n' in example


def test_dockerfile_uses_real_flask_entrypoint_and_health_route():
    docker = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
    assert 'run:app' in docker
    assert '/api/v1/health' in docker
    assert '5000' in docker
    assert 'wsgi:app' not in docker


def test_preflight_runs_without_secrets_or_real_llm():
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'preflight.py')],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Pré-verificação concluída' in result.stdout
