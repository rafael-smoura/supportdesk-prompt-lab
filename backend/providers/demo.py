"""Saídas para demonstração local. Não são resultados de um modelo de IA."""
from backend.providers.base import LLMProvider


class DemoProvider(LLMProvider):
    def generate(self, messages, content_type):
        if content_type == "diagnosis":
            return {
                "hypotheses": ["Instabilidade da conexão ou falha temporária no serviço (a confirmar)"],
                "evidence": ["Existe um relato de falha no acesso, ainda sem verificação técnica"],
                "missing_information": ["Mensagem exata exibida", "Horário da última tentativa"],
                "probable_conclusion": "Não há dados suficientes para estabelecer uma causa confirmada.",
            }
        if content_type == "resolution":
            return {
                "steps": [
                    {"number": 1, "action": "Registrar o erro exibido e o horário da tentativa.", "check": "Mensagem e horário anotados."},
                    {"number": 2, "action": "Verificar se o dispositivo tem acesso a outros sites.", "check": "Acesso externo confirmado ou falhou."},
                ],
                "escalation": "Se persistir, encaminhar ao suporte com o erro e o horário registrados.",
            }
        if content_type == "questions":
            return {"questions": [
                {"priority": 1, "question": "Qual é a mensagem de erro apresentada?", "reason": "Localizar o sintoma principal."},
                {"priority": 2, "question": "Outros sites abrem normalmente?", "reason": "Distinguir conectividade de falha no serviço."},
            ]}
        return {
            "ascii_flow": "[Início]\n  |\n[Há mensagem de erro?]\n  |-- Sim --> [Registrar a mensagem] --> [Acionar suporte]\n  '-- Não --> [Testar outro site] --> [Reavaliar]",
            "next_action": "Registrar o sintoma antes de alterar qualquer configuração.",
        }
