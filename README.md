# SupportDesk Prompt Lab

Aplicação para gerar e comparar respostas de suporte técnico com diferentes versões de prompt. O perfil do cliente (nível técnico, estilo de comunicação e canal) é combinado com um ticket para produzir diagnósticos, procedimentos, perguntas e fluxos de decisão.

O projeto usa Python, Flask, SQLAlchemy e SQLite no backend. A interface é feita em HTML, CSS e JavaScript e é servida pela própria aplicação Flask.

## Execução local

Requer Python 3.11 ou 3.12.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Acesse `http://127.0.0.1:5000`. No Linux ou macOS, ative o ambiente com `source .venv/bin/activate` e copie o exemplo com `cp .env.example .env`.

Por padrão, `.env.example` utiliza o provedor `demo`, que permite testar a aplicação sem uma chave de API. Para gerar respostas com um modelo real, configure as variáveis no `.env`. Exemplo com a GroqCloud:

```dotenv
AI_PROVIDER=openai_compatible
AI_MODEL=openai/gpt-oss-20b
AI_API_URL=https://api.groq.com/openai/v1/chat/completions
AI_API_KEY=SUA_CHAVE
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=1300
AI_TIMEOUT=35
AI_JSON_MODE=true
```

Reinicie o servidor após alterar a configuração. `GET /api/v1/meta` informa o provedor e o modelo ativos. A chave deve permanecer no `.env`, fora do controle de versão.

## Como usar

1. Selecione o perfil do cliente e o ticket na aba **Experimento**.
2. Escolha o tipo de conteúdo: diagnóstico, resolução, perguntas ou fluxograma.
3. Gere uma resposta individual ou compare os prompts **v1** e **v2**.
4. Na aba **Respostas**, consulte o conteúdo estruturado ou o JSON bruto.
5. Para comparar versões, avalie cada resposta nos critérios **clareza**, **adequação ao cliente** e **acionabilidade**, com notas de 1 a 5 e justificativas.
6. Registre a comparação e exporte o JSON. As execuções também ficam disponíveis em **Histórico**.

A comparação mantém cliente, ticket, modelo e configurações iguais; o texto do prompt é a variável testada. As notas são humanas e não são calculadas pelo modelo.

Também existe uma interface por linha de comando:

```powershell
python main.py --customer c1 --ticket t1 --type diagnosis --version v2
python main.py --customer c1 --ticket t1 --type diagnosis --compare
```

## Estrutura

```text
backend/
  api/            Rotas REST
  providers/      Integrações de modelos
  services/       Prompts, geração, validação e comparação
  repositories/   Persistência
  models/         Entidades do banco
frontend/         Interface web
data/             Perfis e tickets JSON
docs/             API, arquitetura e resultado do experimento
samples/          Exemplos JSON e comparação registrada
tests/            Testes automatizados
scripts/          Verificações do projeto
main.py           CLI
run.py            Servidor Flask
```

As execuções são armazenadas em SQLite (`instance/supportdesk.db`) e exportadas em `instance/history/`. Esses arquivos locais não são versionados.

## Testes

```powershell
python -m pytest -q
python scripts/verify_structure.py
python scripts/preflight.py --strict
```

Os testes usam dados controlados e não precisam acessar a API externa. Para conferir a integração, gere uma resposta com o provedor configurado no `.env`.

## Decisões e limitações

A estratégia dos prompts e o método de comparação estão em [`PROMPT_ENGINEERING_NOTES.md`](PROMPT_ENGINEERING_NOTES.md). O contrato REST está em [`docs/API.md`](docs/API.md) e a análise da primeira comparação em [`docs/RESULTADO_DO_EXPERIMENTO.md`](docs/RESULTADO_DO_EXPERIMENTO.md).

O sistema valida a estrutura do JSON, mas não garante a correção técnica do texto gerado. O resultado da comparação é baseado em uma rubrica qualitativa aplicada a um cenário; não demonstra superioridade estatística de um prompt. A aplicação não inclui autenticação de usuários, RAG nem ajuste fino de modelos.

Se a aplicação for publicada, configure `APP_ENV=production`, um `APP_ACCESS_TOKEN` forte e HTTPS. Evite usar dados pessoais reais nos tickets.
