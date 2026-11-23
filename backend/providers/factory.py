from backend.providers.base import ProviderError
from backend.providers.demo import DemoProvider
from backend.providers.http import OpenAICompatibleProvider, GeminiProvider


def create_provider(config):
    mode = config["AI_PROVIDER"]
    if mode == "demo":
        return DemoProvider()
    if mode not in {"gemini", "openai_compatible"}:
        raise ProviderError("AI_PROVIDER deve ser demo, gemini ou openai_compatible", 503)
    if not config.get("AI_API_KEY"):
        raise ProviderError("Configure AI_API_KEY no arquivo .env", 503)
    if mode == "gemini":
        return GeminiProvider(config)
    if not config.get("AI_API_URL", "").startswith("https://"):
        raise ProviderError("AI_API_URL precisa usar HTTPS", 503)
    return OpenAICompatibleProvider(config)
