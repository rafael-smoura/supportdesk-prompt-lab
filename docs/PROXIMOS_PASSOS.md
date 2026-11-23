# Próximos passos para concluir a entrega

Este roteiro separa o que já está implementado no projeto do que depende de contas, credenciais, decisões e avaliação pessoal. **Não confunda exemplos `demo` com evidência de execução de IA real.**

## Etapa A — Rodar no seu computador (obrigatório)

- [ ] Extrair o ZIP e abrir a pasta no VS Code.
- [ ] Confirmar Python 3.11 ou superior: `python --version`.
- [ ] Criar venv no PowerShell: `python -m venv .venv`.
- [ ] Ativar: `.\.venv\Scripts\Activate.ps1`.
- [ ] Instalar: `python -m pip install -r requirements-dev.txt`.
- [ ] Copiar configuração: `Copy-Item .env.example .env`.
- [ ] Iniciar: `python run.py` e abrir `http://127.0.0.1:5000`.
- [ ] Criar um experimento demo v1/v2, avaliar, exportar JSON e conferir `instance/history/`.
- [ ] Executar `python -m pytest -q` e registrar o resultado **verdadeiro** no README se desejar.

Se o PowerShell bloquear a ativação, use `.\.venv\Scripts\python.exe run.py` (funciona mesmo sem ativar a venv).

## Etapa B — Criar uma chave de API (obrigatório para evidência real)

**Caminho sugerido: Gemini Developer API.** A disponibilidade e gratuidade variam conforme modelo, cota e região; confira os termos vigentes.

1. Acesse https://aistudio.google.com/ e faça login.
2. Crie um projeto/chave conforme as instruções do serviço.
3. Confirme quais modelos estão habilitados e os limites de uso em https://ai.google.dev/gemini-api/docs/pricing.
4. Configure `.env` assim:

   ```dotenv
   AI_PROVIDER=gemini
   AI_MODEL=gemini-2.5-flash-lite
   AI_API_KEY=SUA_CHAVE_AQUI
   AI_TEMPERATURE=0.2
   AI_MAX_TOKENS=1300
   AI_JSON_MODE=true
   ```

5. **Não** envie a chave para o GitHub nem compartilhe capturas do `.env`.
6. Reinicie `python run.py`. Na barra lateral deve aparecer `gemini`, não `demo`.
7. Se receber HTTP 404 de modelo indisponível, consulte a lista de modelos liberados no seu projeto e ajuste `AI_MODEL`. Se houver incompatibilidade de JSON mode, experimente `AI_JSON_MODE=false` e reinicie. Não substitua saídas reais por exemplos.

**Alternativa:** API OpenAI-compatible. Use `AI_PROVIDER=openai_compatible`, `AI_API_URL`, `AI_MODEL` e `AI_API_KEY`. Consulte custos antes de executar.

## Etapa C — Comparação obrigatória (essencial, vale boa parte da avaliação)

1. Escolha **um perfil** (ex.: c1) e **um ticket** (ex.: t1). Mantenha ambos fixos.
2. Escolha um tipo (recomendação: diagnóstico, pois explicita hipóteses, evidências e dados faltantes).
3. Clique **Comparar v1 e v2**. Isso gera duas respostas com o mesmo modelo, temperatura, limite de tokens e ticket; a versão do prompt muda.
4. Leia as duas respostas sem atribuir vitória antecipada para v2.
5. Em cada versão, preencha três notas de 1 a 5: clareza, adequação ao nível do cliente e acionabilidade. Explique **o que na resposta motivou a nota**.
6. Salve as avaliações e clique **Salvar comparação em JSON**.
7. Baixe `comparison_{id}.json` e salve **uma cópia revisada** em `samples/comparacao_real_analisada.json` (não envie dados pessoais ou segredos).
8. Atualize `PROMPT_ENGINEERING_NOTES.md` ou crie `docs/RESULTADO_DO_EXPERIMENTO.md` com: modelo exato, data real, configurações, notas, diferenças observadas e limitações.
9. Refaça com outro ticket se quiser um extra; 1 cenário completo é o mínimo.

**Atenção:** o provedor `demo` retorna conteúdo previsível e pode produzir a mesma resposta para as duas versões. Isso **não** comprova superioridade de prompt.

## Etapa D — Git e GitHub (obrigatório histórico verificável)

- [ ] Criar repositório **seu** no GitHub, preferencialmente público apenas depois de revisar dados.
- [ ] Na pasta local: `git init` e `git branch -M main` (se não existir repositório).
- [ ] Conferir `git status` e `git check-ignore .env`; o `.env` deve estar ignorado.
- [ ] Criar seus commits reais por funcionalidades/ajustes efetuados, seguindo `docs/COMMITS_SUGERIDOS.md` apenas como roteiro.
- [ ] Associar repositório: `git remote add origin https://github.com/SEU_USUARIO/NOME_REPO.git`.
- [ ] Enviar: `git push -u origin main` após os commits.
- [ ] Confirmar na aba **Actions** se CI passou (o primeiro push dispara o workflow).
- [ ] Conferir no GitHub que não foram enviados `.env`, chaves ou `instance/history/`.

**Não** altere datas de commit para simular trabalho anterior. O histórico deve representar suas alterações e seu domínio da implementação.

## Etapa E — CI no GitHub (fornecido; ativação depende do push)

O arquivo `.github/workflows/ci.yml` instala as dependências e roda `compileall` + `pytest` nas versões Python 3.11 e 3.12. Você precisa publicar o projeto no GitHub para que o serviço execute. Se um job falhar, abra o log e corrija localmente antes de entregar.

## Etapa F — Deploy (opcional, diferencial)

**Render** (exemplo). Documentação oficial: https://render.com/docs/deploy-flask

1. Crie sua conta no Render e conecte o repositório GitHub.
2. Escolha **New > Web Service** e a branch principal.
3. Configure runtime Python; build command: `pip install -r requirements.txt`.
4. Start command: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 90`.
5. Configure as variáveis de ambiente no painel, **nunca no Git**:

   ```text
   APP_ENV=production
   APP_ACCESS_TOKEN=<uma chave aleatória longa>
   AI_PROVIDER=gemini
   AI_MODEL=<um modelo disponível>
   AI_API_KEY=<chave real>
   AI_TEMPERATURE=0.2
   AI_MAX_TOKENS=1300
   AI_JSON_MODE=true
   ```

6. Faça deploy. Verifique `/api/v1/health` e abra a home. A interface pedirá o `APP_ACCESS_TOKEN` para acessar as outras rotas.
7. **Persistência:** o filesystem de planos gratuitos/efêmeros pode ser apagado em reinícios. Para uma demonstração sem persistência, use `demo` e deixe explícito. Para manter comparações reais em produção, use hospedagem com disco persistente **ou** banco PostgreSQL externo + driver apropriado (não incluído por padrão; adicione `psycopg[binary]` ao `requirements.txt` e teste migrations/URL). Os arquivos JSON também precisam de um volume persistente ou exportação/backup.
8. Se usar IA paga, mantenha o endpoint protegido e monitore o uso. Não divulgue o token no README nem permita que terceiros utilizem a chave inadvertidamente.

**Docker local:** `docker compose up --build -d`; a configuração já inclui volume e healthcheck. Para Render/Railway com Docker, confira os requisitos atuais de porta, volume e variáveis na plataforma escolhida.

## Etapa G — Revisão final antes de enviar

- [ ] Código inicializa com `python run.py` e CLI com `python main.py --compare`.
- [ ] Todas as quatro saídas funcionam com sua API real, não apenas em `demo`.
- [ ] Cache demonstrado: repetir uma entrada devolve `cached: true`.
- [ ] Comparação real completa e avaliada está em `samples/`.
- [ ] É possível explicar o que mudou em v1 e v2 e por que as notas fazem sentido.
- [ ] CI está verde; todas as dependências e comandos do README foram confirmados.
- [ ] Credenciais não foram expostas; GitHub contém commits reais.
- [ ] Limitações estão documentadas e os campos JSON seguem o contrato do edital.
- [ ] Link de deploy (caso feito) funciona sem demonstrar dados pessoais.

## Apresentação curta: o que mostrar em 3 minutos

1. **Problema:** personalizar suporte técnico a partir de perfil/ticket.
2. **Fluxo:** selecionar perfil e ticket, gerar os quatro conteúdos, repetir chamada para demonstrar cache.
3. **Experimento:** apresentar v1 e v2 lado a lado, explicar a rubrica e abrir o JSON salvo.
4. **Arquitetura:** explicar `routes` → `services` → `providers` / `repositories`, model, frontend e banco.
5. **Limitações:** não há autenticação multiusuário, inferência tem custo/cotas, notas são humanas, deploy gratuito pode ser efêmero.

**Status honesto do pacote:** código e documentação estão preparados. Credenciais, consumo de API real, rubricas escritas por você, GitHub/CI online e deploy só podem ser concluídos com seu acesso e sua execução.
