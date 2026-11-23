# Conferência dos requisitos do desafio (PDF, páginas 2–6)

Legenda: **Implementado** = existe no código, requer execução local para validação definitiva; **Pendente externo** = depende de credencial/ação pessoal; **Extra** = não exigido.

| Requisito | Status | Evidência no projeto |
|---|---|---|
| Python e interface mínima CLI | Implementado | `main.py`, `run.py` |
| Perfis (3 a 5) em JSON | Implementado | `data/profiles.json` (4 perfis) |
| Ticket livre ou de catálogo | Implementado | CLI `--text`, frontend, `data/tickets.json` |
| Geração de quatro tipos de conteúdo | Implementado | `services/prompts.py`, `services/validators.py`, `providers/` |
| Prompts distintos por tarefa e versão | Implementado | `build_messages`, `TASKS`, v1/v2 |
| Persona, contexto, decomposição, saída | Implementado | `PROMPT_ENGINEERING_NOTES.md` |
| Provedor de IA real | **Pendente externo** | `providers/http.py` pronto; usuário deve fornecer chave e executar |
| Cache de entradas equivalentes | Implementado | hashes no `GenerationService`, coluna `cache_key` |
| Histórico de gerações em JSON com timestamp | Implementado | `instance/history/generation_ID.json` |
| Duas versões para o mesmo ticket e perfil | Implementado | `/api/v1/experiments`, CLI `--compare` |
| Rubrica fixa de 3 critérios, 1–5, justificativa | Implementado | `services/rubric.py`, frontend |
| Comparação completa salva no histórico JSON | Implementado (mecanismo) | `ComparisonService`, `instance/history/comparison_ID.json` |
| **Evidência real** de v1 e v2 com LLM e rubricas pessoais | **Pendente externo** | preencher `samples/comparacao_real_analisada.json` e `docs/RESULTADO_DO_EXPERIMENTO.md` |
| .env.example sem segredos | Implementado | `.env.example`, `.env_example` |
| requirements e README | Implementado | `requirements*.txt`, `README.md` |
| Diretório samples com JSON | Implementado | `samples/` com exemplos **simulados** |
| Notas de engenharia de prompt | Implementado | `PROMPT_ENGINEERING_NOTES.md` |
| Histórico de commits do próprio candidato | **Pendente externo** | `docs/COMMITS_SUGERIDOS.md`; publicar commits reais |
| Testes automatizados | Implementado (código) | `tests/`; executar na sua máquina e CI |
| Frontend web, API REST, ORM, Docker | Extra | `frontend/`, `backend/api/`, `models/`, Dockerfile |
| CI no GitHub | Pendente ativação | workflow pronto; executar após push |
| Deploy em nuvem | Extra pendente externo | instruções no `docs/PROXIMOS_PASSOS.md` |

**Conclusão:** o pacote cobre o desenho e as funcionalidades exigidas, mas o edital exige **execução real documentada** e um histórico Git legítimo. Não descreva o desafio como 100% finalizado antes dessas duas evidências.
