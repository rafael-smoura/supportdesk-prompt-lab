"""Validação local dos arquivos e das configurações do projeto."""
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


def check_real_comparison(payload):
    """Verify the controlled setup and the completeness of the human rubric."""
    errors = []
    records = payload.get('results', [])
    if not isinstance(records, list) or len(records) != 2:
        return ['A comparação precisa de exatamente duas respostas.']
    if {r.get('prompt_version') for r in records} != {'v1', 'v2'}:
        errors.append('As versões precisam ser v1 e v2.')
    for field in ('scenario_key', 'customer_id', 'ticket', 'content_type', 'provider', 'model', 'settings'):
        values = [r.get(field) for r in records]
        if values[0] != values[1]:
            errors.append(f'O campo {field} deve ser idêntico nas duas respostas.')
    if not all(isinstance(r.get('output'), dict) and r['output'] for r in records):
        errors.append('As duas saídas precisam ter conteúdo.')
    if records[0].get('prompt_hash') == records[1].get('prompt_hash'):
        errors.append('O hash do prompt deve mudar entre as versões.')
    for record in records:
        if record.get('provider') == 'demo' or record.get('model') == 'demo-local':
            errors.append('Uma geração demo não comprova o uso de uma API real.')
        rubric = record.get('evaluation')
        if not isinstance(rubric, dict) or set(rubric) != {'clarity', 'customer_fit', 'actionability'}:
            errors.append('Faltam os três critérios em uma das avaliações.')
            continue
        for key, item in rubric.items():
            if (not isinstance(item, dict) or type(item.get('score')) is not int
                    or not 1 <= item['score'] <= 5 or not isinstance(item.get('justification'), str)
                    or not 20 <= len(item['justification'].strip()) <= 400):
                errors.append(f'Nota ou justificativa inválida em {record.get("prompt_version")}/{key}.')
    if len(payload.get('generation_ids', [])) != 2 or set(payload['generation_ids']) != {r.get('id') for r in records}:
        errors.append('IDs da comparação não correspondem às gerações.')
    return errors


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
        print(f'OK: {len(tracked)} entradas no índice Git, sem .env, banco ou .venv.' if not forbidden else 'ERRO: arquivos privados versionados')

    example = ROOT / '.env.example'
    if not example.is_file():
        errors.append('Falta o arquivo de exemplo .env.example')
    else:
        settings = {}
        for line in example.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                settings[key.strip()] = value.strip()
        for key in ('AI_API_KEY', 'APP_ACCESS_TOKEN'):
            if settings.get(key):
                errors.append(f'{key} não pode ter valor no exemplo')
        if settings.get('AI_PROVIDER') != 'demo':
            errors.append('O exemplo deve iniciar em modo demo')
        if not any('exemplo' in e or 'AI_API_KEY' in e or 'APP_ACCESS_TOKEN' in e for e in errors):
            print('OK: .env.example sem credenciais e com provedor demo.')

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

    real = samples / 'login_comparison.json'
    if real.is_file():
        payload = json.loads(real.read_text(encoding='utf-8'))
        issues = check_real_comparison(payload)
        if issues:
            errors.extend(f'Comparação real: {issue}' for issue in issues)
        else:
            print('OK: comparação real com versões controladas e três justificativas por versão.')
    else:
        print('PENDENTE: comparação real avaliada em samples/login_comparison.json.')

    return errors, real.is_file()


def main():
    parser = argparse.ArgumentParser(description='Pré-verificação antes do push para GitHub')
    parser.add_argument('--strict', action='store_true', help='Exige amostra real avaliada')
    args = parser.parse_args()
    errors, has_real = check()
    if args.strict and not has_real:
        errors.append('Adicione uma comparação com API real antes da entrega final')
    for error in errors:
        print('ERRO:', error, file=sys.stderr)
    if not errors:
        print('Pré-verificação concluída. Execute também pytest e confira o CI.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
