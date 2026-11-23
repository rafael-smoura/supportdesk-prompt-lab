# Comparação de prompts — diagnóstico de acesso

## Cenário

Em 23/11/2026, foram geradas duas respostas para o mesmo ticket: uma cliente não consegue entrar no portal de atendimento e recebe uma mensagem de erro ao fazer login.

| Parâmetro | Valor |
|---|---|
| Perfil | Ana (`c1`), leigo, didático, chat |
| Tipo | Diagnóstico (`diagnosis`) |
| Provedor | GroqCloud (`openai_compatible`) |
| Modelo | `openai/gpt-oss-20b` |
| Temperatura | `0.2` |
| Limite de tokens | `1300` |
| Modo JSON | Ativado |
| Execuções | v1 `#2` e v2 `#1` |

As duas execuções possuem a mesma `scenario_key` e hashes de prompt diferentes. O JSON com as respostas, configurações e rubrica está em [`samples/login_comparison.json`](../samples/login_comparison.json).

## Observações

A **v1** retornou seis hipóteses e oito informações a verificar. Entre elas, pediu logs do servidor e citou certificado SSL. Essas informações podem ajudar um analista técnico, mas não são práticas para uma pessoa leiga atendida por chat.

A **v2** retornou seis hipóteses e seis informações a verificar. Perguntar pelo texto do erro e testar outro navegador são verificações mais próximas do que a cliente pode fazer. Ainda assim, a resposta usa termos como DNS e autenticação de dois fatores sem explicação.

Nenhuma das versões confirma a causa do problema. As duas tratam credenciais e bloqueio de conta como possibilidades, sem evidências suficientes para encerrar o diagnóstico.

## Rubrica registrada

| Critério | v1 | v2 |
|---|---:|---:|
| Clareza | 4 | 3 |
| Adequação ao cliente | 2 | 3 |
| Acionabilidade | 2 | 3 |
| **Média** | **2,67** | **3,00** |

A v2 ficou **0,33 ponto acima da v1** na média registrada. A principal diferença observada está nas informações solicitadas: a segunda resposta pede verificações mais acessíveis, mas ainda não oferece uma sequência de resolução.

As notas representam uma análise qualitativa desse caso, não uma medida automática de qualidade. O teste precisa ser ampliado para outros clientes, tickets e tipos de conteúdo antes de tirar conclusões gerais.
