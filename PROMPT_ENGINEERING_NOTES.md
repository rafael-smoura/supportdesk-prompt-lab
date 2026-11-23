# Engenharia de prompt — decisões e limitações

## Objetivo da experiência

Avaliar se uma instrução mais contextual e restritiva melhora clareza, adequação ao nível técnico e acionabilidade sem alterar o caso analisado nem a configuração do modelo. O sistema produz quatro conteúdos independentes, todos em JSON validado pelo backend.

## Estratégias implementadas

| Estratégia | Aplicação no código |
|---|---|
| Persona | O papel e os limites do analista são definidos na mensagem `system`. |
| Context setting | Identificador e atributos do perfil, canal e texto do ticket aparecem em JSON de contexto. |
| Decomposição | Diagnóstico usa hipóteses, evidências, dados faltantes e conclusão; tarefas diferentes possuem contratos próprios. |
| Formato de saída | Cada tarefa exige um objeto JSON com campos e tipos pré-definidos. |
| Versionamento | `v1` e `v2` são textos distintos; o hash das mensagens fica registrado por execução. |
| Robustez | A v2 delimita fatos, hipóteses e incertezas, orienta linguagem e trata o ticket como dados não confiáveis. |

## As duas versões

**v1 — Base:** papel, tarefa, contexto completo e contrato JSON. Não especifica explicitamente como converter perfil em estilo ou como priorizar decisões seguras.

**v2 — Contextual:** mantém o mesmo cenário e contrato, acrescentando instruções específicas por nível técnico, estilo e canal. Exige distinção entre evidência e hipótese, priorização de passos reversíveis, informação faltante e escalonamento humano quando necessário. A saída deve ser verificável, não o raciocínio interno do modelo.

A hipótese é que v2 seja mais útil para o cliente. Isso só pode ser confirmado **para o cenário testado** depois da execução com modelo real, leitura dos resultados e notas justificadas. O código não presume vencedor.

## Estratégias por conteúdo

**diagnosis:** hypotheses, evidence, missing_information, probable_conclusion. A evidência deve vir do ticket e não de suposições. A conclusão declara incerteza se faltarem dados.

**resolution:** steps (number, action, check) e escalation. Gera um procedimento que pode ser acompanhado e verificado, respeitando risco e perfil.

**questions:** questions (priority, question, reason), máximo de cinco. Prioriza somente dados necessários para progredir.

**flowchart:** ascii_flow e next_action. Representa a sequência de decisões em texto monoespaçado com ramificações.

## Experimento reproduzível

- Mesmo `customer_id`, texto do ticket normalizado, tipo de conteúdo, provedor, modelo, URL quando aplicável, temperatura, limite de tokens e JSON mode.
- A mudança principal é `prompt_version`, registrada com `prompt_hash` e `scenario_key`.
- Avaliar separadamente: clarity, customer_fit, actionability (1–5, cada nota acompanhada de justificativa escrita).
- Comparação persistida no banco e exportada para JSON com saídas completas e avaliações.
- Se duas respostas forem iguais, reconhecer empate; não criar melhoria artificial.

## Atenção ao modo demo

`DemoProvider` é um substituto determinístico usado em desenvolvimento e CI. As respostas vêm de código Python, não de uma LLM. Seus resultados, inclusive as amostras no diretório `samples/`, são **apenas ilustrativos** e não cumprem a evidência de comparação real solicitada no edital.

## Riscos e limitações

- Modelos podem retornar JSON malformado, campos extras, conteúdo incompleto ou alucinar. O validador bloqueia formatos inválidos, mas não confirma veracidade técnica.
- `temperature=0.2` reduz aleatoriedade, mas não torna a saída determinística entre chamadas.
- Uma comparação de um ticket e um avaliador não mede significância; serve para demonstrar método.
- O campo do ticket é texto não confiável; o prompt declara isso, mas instruções adversariais ainda podem afetar modelos.
- Cotas, modelos disponíveis e preços dos provedores podem mudar.
- Para produção, seria necessário observabilidade de latência/custo, avaliação com mais casos, autenticação e tratamento de dados sensíveis.

## Registro posterior da análise real

Preencher `docs/RESULTADO_DO_EXPERIMENTO.md` depois de executar a API e revisar os resultados. Incluir IDs e datas reais, modelo, valores de config, rubricas, justificativas com trechos/observações e a conclusão fundamentada (inclusive se v2 não for melhor).
