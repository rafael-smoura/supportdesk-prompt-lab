# Como executar e avaliar a comparação

## Cenário sugerido

- Perfil `c1`: pessoa leiga, estilo didático, canal chat.
- Ticket `t1`: veja o conteúdo exato em `data/tickets.json`.
- Conteúdo `diagnosis`.
- Prompt `v1` e `v2` via botão **Comparar v1 e v2**.

O objetivo não é obter uma nota alta, mas demonstrar uma comparação justa, reproduzível e explicável.

## Procedimento

1. Configure uma API de IA real com um único modelo e parâmetros fixos.
2. Confira o indicador de provedor: **não** pode aparecer `demo`.
3. Gere ambas as versões no mesmo experimento. Guarde `id`, `timestamp`, `prompt_hash` e `scenario_key`.
4. Confirme que os `scenario_key` são iguais e os `prompt_hash` diferentes.
5. Leia as respostas com atenção, inclusive dados que possam ter sido inventados.
6. Use a rubrica abaixo e explique suas notas com referência concreta aos textos.
7. Clique **Salvar comparação em JSON** e baixe o arquivo. Confira se possui `results` com duas saídas completas e `evaluation` em cada resultado.
8. Copie o JSON sem dados sensíveis para `samples/comparacao_real_analisada.json`.
9. Registre sua interpretação em `docs/RESULTADO_DO_EXPERIMENTO.md`.

## Rubrica fixa (1–5)

| Critério | Pergunta de avaliação |
|---|---|
| Clareza | A resposta pode ser lida sem ambiguidades, com boa organização? |
| Adequação ao nível do cliente | Termos, explicações e profundidade combinam com leigo/intermediário/avançado? |
| Acionabilidade | Cliente ou atendente entende o próximo passo e como verificar seu resultado? |

Escala: 1 = insuficiente; 2 = fraco; 3 = adequado; 4 = bom; 5 = excelente.

### Exemplo de justificativa boa

“A v2 separa as hipóteses das evidências e diz quais informações faltam; isso evita tratar a causa como confirmada.”

### Exemplo de justificativa fraca

“Gostei mais da v2.”

## Fatores de controle

- Mesmo perfil e ticket: sim.
- Mesmo tipo de conteúdo: sim.
- Mesmo provedor e modelo: sim.
- Mesma temperatura, limite de tokens, URL e modo JSON: sim.
- Versão de prompt: varia.
- Executar na mesma sessão ajuda a reduzir mudanças externas de disponibilidade; não garante resultados idênticos.

## O que não fazer

Não copiar a avaliação ilustrativa de `samples/` como se tivesse sido feita sobre resultados reais. Não inventar métricas de custo ou latência. Não afirmar que o modelo raciocinou de certa forma com base em suposto chain of thought. Não afirmar que v2 venceu sem analisar a saída e a rubrica.
