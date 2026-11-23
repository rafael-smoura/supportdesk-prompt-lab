"""Validações de entrada e formato de saída sem bibliotecas adicionais."""
from backend.services.catalog import find_profile

CONTENT_TYPES = ("diagnosis", "resolution", "questions", "flowchart")
PROMPT_VERSIONS = ("v1", "v2")


def validate_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("Envie um objeto JSON")
    customer_id = payload.get("customer_id")
    profile = find_profile(customer_id)
    if profile is None:
        raise ValueError("Perfil inexistente")
    ticket = payload.get("ticket")
    if not isinstance(ticket, str) or not ticket.strip() or len(ticket.strip()) > 5000:
        raise ValueError("O ticket deve ter entre 1 e 5000 caracteres")
    content_type = payload.get("content_type")
    if content_type not in CONTENT_TYPES:
        raise ValueError("content_type inválido")
    version = payload.get("prompt_version", "v2")
    if version not in PROMPT_VERSIONS:
        raise ValueError("prompt_version inválida")
    return profile, ticket.strip(), content_type, version


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 8000


def _str_list(value, max_items=12):
    return isinstance(value, list) and len(value) <= max_items and all(_nonempty(v) for v in value)


def validate_output(content_type, output):
    if not isinstance(output, dict):
        raise ValueError("A IA não retornou um objeto JSON")
    allowed = {
        "diagnosis": {"hypotheses", "evidence", "missing_information", "probable_conclusion"},
        "resolution": {"steps", "escalation"},
        "questions": {"questions"},
        "flowchart": {"ascii_flow", "next_action"},
    }[content_type]
    if set(output) != allowed:
        raise ValueError("O JSON retornado não segue o contrato de campos")
    if content_type == "diagnosis":
        valid = all(_str_list(output[k]) for k in ("hypotheses", "evidence", "missing_information")) and _nonempty(output["probable_conclusion"])
    elif content_type == "resolution":
        steps = output["steps"]
        valid = (isinstance(steps, list) and 1 <= len(steps) <= 10 and all(
            isinstance(s, dict) and set(s) == {"number", "action", "check"}
            and type(s["number"]) is int and s["number"] == i
            and _nonempty(s["action"]) and _nonempty(s["check"])
            for i, s in enumerate(steps, 1)) and _nonempty(output["escalation"]))
    elif content_type == "questions":
        questions = output["questions"]
        valid = (isinstance(questions, list) and 1 <= len(questions) <= 5 and all(
            isinstance(q, dict) and set(q) == {"priority", "question", "reason"}
            and type(q["priority"]) is int and q["priority"] == i
            and _nonempty(q["question"]) and _nonempty(q["reason"])
            for i, q in enumerate(questions, 1)))
    else:
        valid = _nonempty(output["ascii_flow"]) and _nonempty(output["next_action"])
    if not valid:
        raise ValueError("O formato do JSON não atende ao contrato do tipo de conteúdo")
    return output
