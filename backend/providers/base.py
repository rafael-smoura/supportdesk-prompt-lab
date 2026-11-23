from abc import ABC, abstractmethod


class ProviderError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages, content_type):
        """Devolve um dicionário Python, ainda sujeito à validação de contrato."""
