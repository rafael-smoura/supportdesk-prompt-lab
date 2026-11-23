# Prompt engineering

## Problema

O nível de conhecimento e o canal de atendimento mudam a forma como uma orientação técnica deve ser apresentada. O experimento compara um prompt básico (**v1**) com uma versão que explicita como usar o perfil do cliente (**v2**).

A hipótese é que uma instrução mais específica produza respostas mais adequadas sem perder a estrutura do diagnóstico.

## Construção dos prompts

Os prompts ficam em `backend/services/prompts.py`. Para cada execução, o backend combina o perfil, o ticket e o tipo de resposta solicitado.

| Técnica | Como foi usada |
|---|---|
| Persona prompting | Define a função do assistente de suporte e os limites do atendimento. |
| Context setting | Inclui nível técnico, estilo de comunicação, canal e descrição do problema. |
| Decomposição | Separa hipóteses, evidências, informações ausentes e conclusão no diagnóstico. |
| Output formatting | Define os campos JSON obrigatórios para cada tipo de resposta. |
| Versionamento | Identifica `v1` e `v2` e registra um hash do prompt utilizado. |

**v1:** usa o contexto disponível e exige o formato de saída, com poucas instruções sobre adaptação de linguagem.

**v2:** acrescenta regras por nível técnico e canal, pede distinção entre fatos e possibilidades e orienta o uso de ações simples e verificáveis. O ticket é tratado como dado de entrada, não como uma fonte de instruções para o sistema.

## Tipos de conteúdo

- `diagnosis`: `hypotheses`, `evidence`, `missing_information`, `probable_conclusion`.
- `resolution`: `steps` com `number`, `action` e `check`, além de `escalation`.
- `questions`: perguntas com `priority`, `question` e `reason`.
- `flowchart`: `ascii_flow` e `next_action`.

Cada tipo tem uma instrução específica, mas reutiliza o contexto e as regras gerais. A validação do JSON acontece antes do registro da execução.

## Método de comparação

As duas versões recebem o mesmo perfil, ticket, tipo de conteúdo, provedor, modelo e parâmetros. O backend registra `scenario_key`, `prompt_hash` e as configurações da chamada. A comparação exige versões diferentes e o mesmo cenário.

A rubrica usa três critérios, com notas inteiras de 1 a 5:

| Critério | Pergunta |
|---|---|
| Clareza | O texto é organizado e compreensível? |
| Adequação | A linguagem e o nível de detalhe combinam com o cliente? |
| Acionabilidade | Fica claro o que fazer a seguir? |

Cada nota precisa de uma justificativa ligada ao conteúdo da resposta. A média é simples, com o mesmo peso para os três critérios.

A comparação registrada em [`samples/login_comparison.json`](samples/login_comparison.json) utiliza respostas geradas pela GroqCloud com `openai/gpt-oss-20b`. A análise está em [`docs/RESULTADO_DO_EXPERIMENTO.md`](docs/RESULTADO_DO_EXPERIMENTO.md).

## Limitações

- A temperatura reduzida não elimina variações nas respostas.
- O validador garante a estrutura, mas não verifica se um diagnóstico está correto.
- A avaliação de um cenário não basta para afirmar que uma versão é melhor em qualquer situação.
- O modo `demo` serve apenas para desenvolvimento e testes, sem chamada a um modelo externo.
- O sistema não recupera documentos externos. RAG seria útil para consultar manuais ou procedimentos internos, desde que fosse possível verificar a origem das informações e avaliar a fidelidade das respostas.
