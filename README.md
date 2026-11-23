# SupportDesk Prompt Lab

Protótipo de atendimento técnico personalizado com comparação controlada de versões de prompt. Recebe um perfil de cliente e um ticket, gera quatro tipos de conteúdo, registra a execução e permite que o avaliador atribua notas com justificativas.

**Escopo:** desafio técnico de estágio em IA e Engenharia de Prompt. A aplicação usa uma interface web, uma CLI, Flask, SQLAlchemy e exportações JSON. A arquitetura prioriza o experimento de prompt, não funcionalidades de um help desk corporativo.

> **Importante:** o provedor `demo` usa saídas predefinidas e **não consulta IA**. Para comprovar o requisito de comparação real do desafio, selecione `gemini` ou `openai_compatible` e avalie respostas efetivas de uma LLM. Os arquivos de `samples/` são ilustrativos.

## 1. Início rápido no Windows

Requisitos: Python 3.11+ e pip.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python run.py
```

Acesse http://127.0.0.1:5000. O `.env.example` inicia em `AI_PROVIDER=demo` e dispensa chave de API. **Se já tiver um `.venv` e um `.env` funcionando, não precisa recriá-los**: basta atualizar os arquivos alterados e executar os testes.

No Linux/macOS, use `source .venv/bin/activate` e `cp .env.example .env`.

Para testar a CLI:

```powershell
python main.py --customer c1 --ticket t1 --type diagnosis --version v2
python main.py --customer c1 --ticket t1 --type diagnosis --compare
```

## 2. Ativar uma API de IA

Edite `.env`. Exemplo Gemini (modelo exemplificativo, confirme disponibilidade na sua conta):

```dotenv
AI_PROVIDER=gemini
AI_MODEL=gemini-2.5-flash-lite
AI_API_KEY=SUA_CHAVE_DO_GOOGLE_AI_STUDIO
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=1300
```

Para serviço compatível com Chat Completions:

```dotenv
AI_PROVIDER=openai_compatible
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-4o-mini
AI_API_KEY=SUA_CHAVE
```

Reinicie `python run.py` após alterar o `.env`. Custos, cotas e modelos disponíveis variam por provedor. O modo `AI_JSON_MODE=true` solicita JSON quando suportado; se o modelo negar esse parâmetro, teste `AI_JSON_MODE=false` (o prompt ainda exige JSON).

**Nunca** coloque credenciais no código, no frontend, em arquivos de exemplo ou em commits. A chave é enviada ao provedor **pelo backend**.

## 3. Usar a interface

1. Selecione um dos quatro perfis e um ticket de exemplo (ou edite o texto do ticket).
2. Escolha **Diagnóstico**, **Resolução**, **Perguntas** ou **Fluxograma**.
3. Use **Gerar resposta** para uma versão ou **Comparar v1 e v2** para produzir as duas.
4. Leia cada resposta e atribua notas de 1 a 5 para **clareza**, **adequação ao cliente** e **acionabilidade**, com uma justificativa curta em cada campo.
5. Clique em **Salvar comparação em JSON**. Baixe o arquivo pela interface ou consulte `instance/history/`.

Em modo `demo`, as respostas são simuladas e a avaliação é útil apenas para demonstrar o fluxo. Em modo de API real, o resultado serve de evidência **somente depois de analisado** e justificado por você.

## 4. Rodar testes

```powershell
python -m pytest -q
python -m compileall -q backend main.py run.py
python scripts/preflight.py
```

Os testes não consomem créditos de IA: a configuração é forçada para `demo` ou adaptadores HTTP simulados.

Checagem estrutural sem instalar dependências: `python scripts/verify_structure.py`. O registro do que foi possível validar neste ambiente está em `docs/VALIDACAO_NESTE_AMBIENTE.md`.

## 5. Docker

```powershell
Copy-Item .env.example .env
# Edite o .env conforme necessário.
docker compose up --build -d
docker compose logs -f
```

Interface: http://127.0.0.1:5000. Os dados ficam em um volume nomeado (`supportdesk_data`). Para parar: `docker compose down`. Não use `docker compose down -v` se quiser preservar o histórico.

## 6. Organização do projeto

```text
backend/
  api/routes.py                 HTTP controllers (API REST)
  config.py                     Variáveis de ambiente
  models/entities.py            ORM SQLAlchemy
  providers/                    Adapters demo, Gemini, OpenAI-compatible
  repositories/                 Consultas de banco
  services/                     Casos de uso, prompts, rubricas, exportação
frontend/                       HTML, CSS e JavaScript sem framework
 data/                          Perfis e tickets em JSON
 docs/                          Arquitetura, experimentos, próximos passos
 samples/                       Saídas ilustrativas (não são provas de LLM)
 tests/                         Unitários e integração de API
 instance/                      SQLite e arquivos JSON (não versionados)
 .github/workflows/ci.yml       Pipeline CI
 main.py                        CLI
 run.py                         Entry point Flask/Gunicorn
```

A abordagem é **MVC adaptado para API**: `models/` representa o Model, `api/routes.py` o Controller, `frontend/` a View. Casos de uso ficam em `services/`, abstrações de serviços externos em `providers/` e acesso ao banco em `repositories/`.

## 7. Endpoints REST

Todos sob `/api/v1`:

| Método | Rota | Objetivo |
|---|---|---|
| GET | `/health` | Verificação de saúde |
| GET | `/meta` | Provedor e configurações públicas |
| GET | `/profiles` | Perfis cadastrados |
| GET | `/tickets` | Tickets cadastrados |
| POST | `/runs` | Gerar uma versão |
| POST | `/experiments` | Gerar v1 + v2 no mesmo cenário |
| GET | `/runs` | Consultar execuções |
| GET | `/runs/{id}` | Obter execução |
| PUT | `/runs/{id}/evaluation` | Registrar rubrica humana |
| POST | `/comparisons` | Comparar duas execuções avaliadas |
| GET | `/comparisons` | Listar comparações |
| GET | `/comparisons/{id}` | Recuperar comparação completa |
| GET | `/runs/{id}/export` | Baixar JSON individual |
| GET | `/comparisons/{id}/export` | Baixar JSON comparativo |

Exemplo de geração:

```json
{"customer_id":"c1","ticket":"O portal mostra erro 403 ao entrar.","content_type":"diagnosis","prompt_version":"v2"}
```

Exemplo de comparação após atribuir as rubricas:

```json
{"generation_ids":[1,2]}
```

Consulte `docs/API.md` para exemplos completos de chamadas e rubrica.

## 8. Cache, histórico e condições do experimento

A chave de cache usa SHA-256 do cenário, das mensagens do prompt e das configurações do modelo. Não armazena nem inclui a chave de API. Uma comparação só é aceita quando as execuções têm o mesmo perfil, ticket, tipo de conteúdo, provedor, modelo, parâmetros e URL aplicável. Somente a versão do prompt varia.

As execuções são armazenadas em SQLite e exportadas como `generation_{id}.json`; comparações avaliadas são exportadas como `comparison_{id}.json`. Dados do diretório `instance/` não são enviados ao Git por padrão.

## 9. Segurança e limitações

- API key existe somente no servidor; não há login de usuários nem JWT porque o escopo é um protótipo de demonstração.
- Para deploy público, defina `APP_ENV=production` e `APP_ACCESS_TOKEN` forte. O servidor exige esse token e a interface solicita o valor ao operador. Use HTTPS.
- O sistema não possui controle de quotas por usuário; **não publique um endpoint de geração desprotegido com uma chave paga**.
- O frontend e API são servidos na mesma origem para evitar dependência de CORS e simplificar o deploy.
- `db.create_all()` inicializa o esquema; para evoluções reais de banco, o próximo passo é utilizar migrations.
- SQLite é suficiente para o protótipo local. Em hospedagem com filesystem temporário, o histórico pode desaparecer a cada redeploy.
- A qualidade de v1 e v2 é julgada por uma rubrica humana; a aplicação **não atribui notas automaticamente**.
- A aplicação não solicita nem registra o raciocínio interno detalhado do modelo.

## 10. Histórico Git incluído e publicação no GitHub

Este ZIP inclui a pasta oculta `.git/` e commits **reais de preparação do pacote**, registrados na data em que foram feitos, sob a autoria técnica `SupportDesk Package Setup`. **Não são commits antigos do candidato nem um histórico remoto do GitHub.** Ao extrair o ZIP, confirme `Test-Path .git`, consulte `git log --oneline` e configure seu nome/e-mail para seus próximos commits. Veja `docs/GIT_E_GITHUB.md` para o passo a passo de publicação sem reescrever histórico.

Antes de publicar, rode `python scripts/preflight.py` para checar segredos, Docker e exemplos. Depois de gerar e avaliar uma comparação com IA real, use `python scripts/preflight.py --strict`.

## 11. Documentação complementar

- `docs/PROXIMOS_PASSOS.md`: instruções exatas do que fazer com API, experimento, GitHub e Render.
- `docs/EXPERIMENTO_GUIADO.md`: condução da comparação justa e registro da rubrica.
- `docs/ARQUITETURA.md`: componentes e decisões SOLID.
- `PROMPT_ENGINEERING_NOTES.md`: versões, segurança e limitações de prompt.
- `docs/API.md`: contratos REST com exemplos.
- `docs/CHECKLIST_EDITAL.md`: aderência às exigências, inclusive pendências externas.
- `docs/GIT_E_GITHUB.md`: publicar o histórico local verdadeiro e criar commits próprios.
- `docs/HISTORICO_GIT_REAL.md`: resumo dos commits criados durante a preparação deste pacote.
- `docs/COMMITS_SUGERIDOS.md`: sugestões para trabalhos futuros, não histórico retroativo.
- `CHANGELOG.md`: mudanças efetivamente realizadas nesta revisão.

## Referências

- Enunciado do desafio: `Desafio_Tecnico_Estagio_IA_Engenharia_de_Prompt.pdf` (fornecido separadamente).
- Gemini: https://ai.google.dev/gemini-api/docs
- Render + Flask: https://render.com/docs/deploy-flask
- GitHub Actions Python: https://docs.github.com/en/actions/tutorials/build-and-test-code/python
