# Arquitetura e decisões de projeto

## Visão de componentes

```text
                    ┌─────────────────────┐
                    │ frontend/ HTML/CSS/JS│
                    └──────────┬──────────┘
                               │ HTTP /api/v1
                    ┌──────────▼──────────┐
                    │ backend/api/routes  │  Controller
                    └──────────┬──────────┘
                               │
                 ┌─────────────▼───────────────┐
                 │ services/                   │
                 │ generation, comparison,     │
                 │ prompts, rubric, validators │
                 └───────┬──────────────┬──────┘
                         │              │
                ┌────────▼────────┐ ┌───▼─────────────┐
                │ providers/      │ │ repositories/   │
                │ demo/gemini/    │ │ SQLAlchemy ORM  │
                │ openai_compat   │ └───┬─────────────┘
                └─────────────────┘     │
                                    ┌───▼──────────┐
                                    │ SQLite       │
                                    │ + JSON files │
                                    └──────────────┘
```

MVC é adotado como convenção: `models` = modelos, `api` = controllers, `frontend` = view. `services` contém casos de uso, evitando lógica de negócio dentro dos endpoints.

## Responsabilidades

- `routes.py`: entradas e saídas HTTP, códigos de status, controle de acesso opcional.
- `GenerationService`: valida cenário, aplica versão de prompt, calcula hash de cache, chama provedor, valida JSON e salva.
- `ComparisonService`: exige mesmo cenário e versões diferentes, guarda avaliação humana e cria artefato consolidado.
- `providers/`: classes que implementam a interface `LLMProvider` (Dependency Inversion).
- `repositories/`: acesso ao banco isolado de regras de prompt.
- `exporter.py`: escrita atômica de arquivos JSON.
- `frontend/`: estado da interface; não contém chaves de API.

## SOLID na prática, sem excesso

1. **S:** cada módulo possui responsabilidade bem definida (prompts, provedor, geração, avaliação, exportação).
2. **O:** é possível adicionar `AnotherProvider` implementando `LLMProvider` e mapeando na fábrica, sem alterar a lógica da geração.
3. **L:** implementações do provedor devolvem dicionários submetidos ao mesmo validador.
4. **I:** a interface `LLMProvider` possui apenas a operação relevante `generate`.
5. **D:** `GenerationService` pode receber provedor e repositório injetados nos testes.

## MVC, não arquitetura hexagonal completa

O projeto usa adaptação leve de MVC. Não adota camadas e DTOs para cada entidade porque isso aumentaria a quantidade de arquivos sem beneficiar o experimento. O repositório é um detalhe de infraestrutura; o serviço centraliza regras.

## Cache e reprodutibilidade

`scenario_key = SHA256(perfil JSON + ticket normalizado + tipo + provedor + modelo + configurações)`.

`prompt_hash = SHA256(mensagens finais do prompt)`.

`cache_key = SHA256(scenario_key + prompt_hash)`.

Mudanças no texto de prompt, no modelo ou em parâmetros geram outra chave. O token secreto não faz parte da chave e não é persistido. A mesma entrada e mesmas configurações podem ser reutilizadas sem nova cobrança. O modo demo usa o mesmo mecanismo.

## Limites da comparação

Comparação aceita dois registros avaliados com a mesma `scenario_key` e versões distintas (`v1`, `v2`). A rubrica usa três critérios igualmente ponderados. A média ajuda na apresentação, mas é uma avaliação subjetiva de um caso, não métrica estatística ou benchmark de LLM.

## Banco e arquivos

- `Generation`: contexto, versão, configuração, hashes, resposta e avaliação.
- `Comparison`: IDs das duas execuções, chave do cenário, média de notas e diferença.
- `instance/history/generation_ID.json`: exportação de cada execução.
- `instance/history/comparison_ID.json`: comparação com **ambas** as saídas e rubricas.

`db.create_all()` simplifica o setup de estágio. Atualizações de esquema devem futuramente usar Flask-Migrate/Alembic. O sistema não promete transação atômica distribuída entre SQLite e filesystem: falhas de gravação JSON podem precisar de reexportação.

## Segurança e limites operacionais

- Senhas e chaves nunca devem ser solicitadas no ticket nem enviadas ao frontend.
- Tokens do provedor só são enviados em HTTPS pelo servidor.
- `APP_ACCESS_TOKEN` protege endpoints da aplicação quando configurado; não substitui autenticação multiusuário.
- Requisições são limitadas a 15 KB e tickets a 5.000 caracteres.
- Resultado JSON é validado (campos e tipos) antes de persistir.
- Não existe controle de custo, quota por usuário ou ferramenta de observabilidade avançada.
- Aplicação não deve ser usada com dados sensíveis reais ou como sistema crítico de suporte.
