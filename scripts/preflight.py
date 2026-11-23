"""Checagens rápidas de entrega: sem dependências externas e sem chamadas de IA."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked_files():
    if not (ROOT / '.git').is_dir():
        return None
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True)
    return [Path(name.decode('utf-8')) for name in result.stdout.split(b'\0') if name]


def check():
    errors = []
    tracked = tracked_files()
    if tracked is None:
        print('AVISO: não há repositório Git local; histórico ainda não verificável.')
    else:
        forbidden = [str(p) for p in tracked if (
            p == Path('.env') or '.venv' in p.parts or 'venv' in p.parts
            or 'instance' in p.parts and p.name != '.gitkeep'
            or p.suffix.lower() in {'.db', '.sqlite3', '.pem', '.key'}
        )]
        if forbidden:
            errors.append('Arquivos privados versionados: ' + ', '.join(forbidden))
        print(f'OK: {len(tracked)} arquivos versionados, sem .env, banco ou .venv.' if not forbidden else 'ERRO: arquivos privados versionados')

    examples = [(ROOT / '.env.example'), (ROOT / '.env_example')]
    if not all(path.is_file() for path in examples):
        errors.append('Falta um dos exemplos de ambiente')
    else:
        content = [p.read_text(encoding='utf-8') for p in examples]
        if content[0] != content[1]:
            errors.append('.env.example e .env_example devem ser iguais')
        settings = {}
        for line in content[0].splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                settings[key.strip()] = value.strip()
        for key in ('AI_API_KEY', 'APP_ACCESS_TOKEN'):
            if settings.get(key):
                errors.append(f'{key} não pode ter valor no exemplo')
        if settings.get('AI_PROVIDER') != 'demo':
            errors.append('O exemplo deve iniciar em modo demo')
        print('OK: exemplos de ambiente sem credenciais.' if not any('exemplo' in e or 'AI_API_KEY' in e or 'APP_ACCESS_TOKEN' in e for e in errors) else 'ERRO: exemplos de ambiente')

    docker = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
    for expected in ('run:app', '5000', '/api/v1/health'):
        if expected not in docker:
            errors.append(f'Dockerfile não referencia {expected}')
    if not any('Dockerfile' in e for e in errors):
        print('OK: Dockerfile usa run:app, porta 5000 e healthcheck correto.')

    samples = ROOT / 'samples'
    for sample in samples.glob('*.json'):
        try:
            json.loads(sample.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError) as exc:
            errors.append(f'JSON inválido em {sample.name}: {exc}')

    real = samples / 'comparacao_real_analisada.json'
    if real.is_file():
        payload = json.loads(real.read_text(encoding='utf-8'))
        results = payload.get('results', [])
        if (len(results) != 2 or
                {r.get('prompt_version') for r in results} != {'v1', 'v2'} or
                any(r.get('provider') == 'demo' or not r.get('evaluation') for r in results)):
            errors.append('Comparação real incompleta: revise versões, provedor e rubricas')
        else:
            print('OK: amostra de comparação real encontrada (revise justificativas manualmente).')
    else:
        print('PENDENTE: comparação real avaliada em samples/comparacao_real_analisada.json.')

    return errors, real.is_file()


def main():
    parser = argparse.ArgumentParser(description='Pré-verificação antes do push para GitHub')
    parser.add_argument('--strict', action='store_true', help='Exige amostra real avaliada')
    args = parser.parse_args()
    errors, has_real = check()
    if args.strict and not has_real:
        errors.append('Execute a comparação com API real antes da entrega final')
    for error in errors:
        print('ERRO:', error, file=sys.stderr)
    if not errors:
        print('Pré-verificação concluída. Execute também pytest e confira o CI.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
