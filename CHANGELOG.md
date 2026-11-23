# Registro de alterações

Este arquivo resume mudanças no **pacote preparado em 23/11/2026**. O registro oficial de alterações é o histórico Git (`git log`). Não representa uma cronologia anterior de desenvolvimento do candidato.

## Revisão atual

- Importação do projeto funcional e da correção de exportação JSON no Windows.
- Ajuste do `Dockerfile` para usar `run:app`, porta `5000` e rota `/api/v1/health`, em conformidade com o Flask e o Compose.
- Alinhamento de `.env.example` e `.env_example` com todas as opções principais do backend, sem credenciais reais.
- Adição de pré-verificação de arquivos versionados, exemplos de ambiente, Docker e amostras JSON.
- Ajuste da checagem estrutural para permitir um `.env` **local não versionado** e uma futura comparação real em `samples/`.
- Guia de Git/GitHub com comandos para Windows, autoria dos commits e verificação de CI.

## O que ainda não é resultado concluído

- Chamada real a uma LLM com chave própria e evidência de comparação avaliada.
- Publicação no GitHub e execução do workflow online.
- Deploy em nuvem.
