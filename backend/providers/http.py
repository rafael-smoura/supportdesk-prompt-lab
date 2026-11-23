"""Adaptadores HTTP. Uma interface comum permite trocar o provedor sem mudar o serviço."""
import json
import requests
from backend.providers.base import LLMProvider, ProviderError

MAX_RESPONSE_BYTES = 100_000


def _parse_json(text):
    try:
        result = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise ProviderError("A API retornou texto que não é JSON válido") from exc
    if not isinstance(result, dict):
        raise ProviderError("A API retornou um JSON que não é um objeto")
    return result


def _request(session, url, *, headers, payload, timeout):
    try:
        response = session.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.Timeout as exc:
        raise ProviderError("Tempo de resposta da API esgotado", 504) from exc
    except requests.RequestException as exc:
        raise ProviderError("Falha de conexão com o provedor", 502) from exc
    if response.status_code in (429,):
        raise ProviderError("Limite de requisições do provedor atingido", 429)
    if response.status_code in (401, 403):
        raise ProviderError("Credencial de API inválida ou sem permissão", 502)
    if not response.ok:
        raise ProviderError(f"O provedor retornou HTTP {response.status_code}", 502)
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ProviderError("Resposta do provedor excede o tamanho permitido")
    try:
        return response.json()
    except ValueError as exc:
        raise ProviderError("O provedor retornou uma resposta HTTP inválida") from exc


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, config, session=None):
        self.config = config
        self.session = session or requests.Session()

    def generate(self, messages, content_type):
        body = {
            "model": self.config["AI_MODEL"],
            "messages": messages,
            "temperature": self.config["AI_TEMPERATURE"],
            "max_tokens": self.config["AI_MAX_TOKENS"],
        }
        if self.config["AI_JSON_MODE"]:
            body["response_format"] = {"type": "json_object"}
        payload = _request(
            self.session, self.config["AI_API_URL"],
            headers={"Authorization": f"Bearer {self.config['AI_API_KEY']}", "Content-Type": "application/json"},
            payload=body, timeout=self.config["AI_TIMEOUT"],
        )
        try:
            raw = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Estrutura de resposta não reconhecida (OpenAI-compatible)") from exc
        return _parse_json(raw)


class GeminiProvider(LLMProvider):
    """API REST generateContent; formato JSON controlado por prompt e responseMimeType."""
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, config, session=None):
        self.config = config
        self.session = session or requests.Session()

    def generate(self, messages, content_type):
        model = self.config["AI_MODEL"].replace("models/", "")
        if not model or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for c in model):
            raise ProviderError("AI_MODEL inválido para Gemini", 503)
        data = {
            "systemInstruction": {"parts": [{"text": messages[0]["content"]}]},
            "contents": [{"role": "user", "parts": [{"text": messages[1]["content"]}]}],
            "generationConfig": {
                "temperature": self.config["AI_TEMPERATURE"],
                "maxOutputTokens": self.config["AI_MAX_TOKENS"],
            },
        }
        # Endpoint generateContent é amplamente suportado; se o modelo não aceitar
        # responseMimeType, mude AI_JSON_MODE para false sem alterar os prompts.
        if self.config["AI_JSON_MODE"]:
            data["generationConfig"]["responseMimeType"] = "application/json"
        payload = _request(
            self.session, f"{self.BASE_URL}/{model}:generateContent",
            headers={"x-goog-api-key": self.config["AI_API_KEY"], "Content-Type": "application/json"},
            payload=data, timeout=self.config["AI_TIMEOUT"],
        )
        try:
            parts = payload["candidates"][0]["content"]["parts"]
            raw = "".join(part.get("text", "") for part in parts)
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Estrutura de resposta não reconhecida (Gemini)") from exc
        return _parse_json(raw)
