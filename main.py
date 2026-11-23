"""CLI: execução e comparação reprodutível sem necessidade de interface web."""
import argparse
import json
import sys
from pathlib import Path
from backend import create_app
from backend.services.catalog import find_ticket
from backend.services.comparison import ComparisonService
from backend.services.generation import GenerationService
from backend.services.validators import CONTENT_TYPES, PROMPT_VERSIONS
from backend.providers.base import ProviderError


def main(argv=None):
    parser = argparse.ArgumentParser(description="SupportDesk Prompt Lab - linha de comando")
    parser.add_argument("--customer", default="c1", help="Identificador em data/profiles.json")
    parser.add_argument("--ticket", default="t1", help="ID em data/tickets.json")
    parser.add_argument("--text", help="Texto livre substituindo o ticket do catálogo")
    parser.add_argument("--type", default="diagnosis", choices=CONTENT_TYPES)
    parser.add_argument("--version", default="v2", choices=PROMPT_VERSIONS)
    parser.add_argument("--compare", action="store_true", help="Gera v1 e v2 para o mesmo cenário")
    parser.add_argument("--evaluations", type=Path, help="JSON com rubricas v1 e v2; válido apenas com --compare")
    args = parser.parse_args(argv)
    if args.evaluations and not args.compare:
        parser.error("--evaluations exige --compare")
    selected = find_ticket(args.ticket)
    ticket = args.text if args.text is not None else (selected["description"] if selected else None)
    if ticket is None:
        parser.error("Ticket desconhecido. Use --text ou consulte data/tickets.json")
    app = create_app()
    with app.app_context():
        service = GenerationService(app.config)
        records = []
        try:
            for version in (("v1", "v2") if args.compare else (args.version,)):
                run, cached = service.generate({
                    "customer_id": args.customer, "ticket": ticket,
                    "content_type": args.type, "prompt_version": version,
                })
                records.append(run)
                print(json.dumps({"cached": cached, "record": run.to_dict()}, indent=2, ensure_ascii=False))
            if args.compare and args.evaluations:
                evaluations = json.loads(args.evaluations.read_text(encoding="utf-8"))
                reviewer = ComparisonService()
                for run in records:
                    reviewer.evaluate(run.id, evaluations[run.prompt_version])
                comparison = reviewer.compare([run.id for run in records])
                print(json.dumps({"comparison": comparison}, indent=2, ensure_ascii=False))
            elif args.compare:
                print("\nPróxima etapa: avalie v1 e v2 pelo frontend ou use --evaluations arquivo.json.")
            print("Histórico JSON: instance/history/ | Banco: instance/supportdesk.db")
        except (ValueError, LookupError, OSError, KeyError, ProviderError) as exc:
            print(f"Erro: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
