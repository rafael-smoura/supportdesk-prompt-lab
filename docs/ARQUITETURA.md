# Arquitetura

O sistema tem uma interface web e uma CLI que compartilham os serviços do backend Flask. O backend monta os prompts, chama o provedor configurado, valida a resposta e salva as execuções.

```text
Frontend / CLI
      |
      v
Flask API (/api/v1)
      |
      v
Services (prompts, geração, comparação, validação)
      |                          |
      v                          v
Providers (LLM)         Repositories (SQLAlchemy)
                                 |
                                 v
                               SQLite
```

## Organização

- `backend/api/routes.py`: valida requisições HTTP e devolve respostas padronizadas.
- `backend/services/prompts.py`: monta os prompts por versão e tipo de conteúdo.
- `backend/services/generation.py`: controla as execuções, o cache e a validação da saída.
- `backend/services/comparison.py`: reúne duas gerações do mesmo cenário e calcula as médias das rubricas.
- `backend/providers/`: acesso ao modo local, Gemini ou APIs compatíveis com OpenAI.
- `backend/repositories/`: persistência via SQLAlchemy.
- `backend/models/`: entidades `Generation` e `Comparison`.
- `frontend/`: telas de geração, respostas, avaliação e histórico.

## Cache

O sistema utiliza uma chave de cenário com os dados do cliente, ticket, tarefa, provedor, modelo e parâmetros. O hash das mensagens do prompt também entra na chave de cache. Assim, chamadas equivalentes podem reutilizar um resultado já salvo.

Os segredos do arquivo `.env` não entram nos hashes nem nas exportações. Cada geração também fica disponível em `instance/history/` como JSON.

## Comparação

A comparação aceita duas execuções avaliadas com versões distintas e a mesma chave de cenário. Cada critério recebe uma nota de 1 a 5 e uma justificativa. Se uma avaliação for editada, o resumo da comparação é atualizado na próxima consulta e na exportação.

## Limites

O uso de SQLite simplifica a execução local, mas migrações seriam necessárias para evoluir o esquema em produção. A aplicação não possui login multiusuário, medição de custo por requisição ou base de documentos para RAG. Uma resposta que respeite o contrato JSON ainda pode conter hipóteses incorretas.
