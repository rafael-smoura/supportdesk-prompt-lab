CRITERIA = ("clarity", "customer_fit", "actionability")


def validate_rubric(payload):
    if not isinstance(payload, dict) or set(payload) != set(CRITERIA):
        raise ValueError("A rubrica exige clarity, customer_fit e actionability")
    result = {}
    for criterion in CRITERIA:
        item = payload[criterion]
        if not isinstance(item, dict) or set(item) != {"score", "justification"}:
            raise ValueError(f"Critério inválido: {criterion}")
        score = item["score"]
        justification = item["justification"]
        if (type(score) is not int or not 1 <= score <= 5 or not isinstance(justification, str)
                or not 5 <= len(justification.strip()) <= 400):
            raise ValueError(f"Nota ou justificativa inválida em {criterion}")
        result[criterion] = {"score": score, "justification": justification.strip()}
    return result


def average(evaluation):
    return round(sum(evaluation[c]["score"] for c in CRITERIA) / len(CRITERIA), 2)
