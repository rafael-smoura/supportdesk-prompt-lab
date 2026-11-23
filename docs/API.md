# Referência rápida da API REST

Prefixo: `http://127.0.0.1:5000/api/v1`. O frontend utiliza a mesma origem. Se `APP_ACCESS_TOKEN` estiver configurado, envie `X-Access-Token` em todas as rotas, exceto health.

## POST /runs

```json
{
  "customer_id": "c1",
  "ticket": "O sistema mostra erro ao autenticar.",
  "content_type": "diagnosis",
  "prompt_version": "v2"
}
```

Resposta: `201` novo registro ou `200` cache, contendo `record`, `cached`, `export`. Tipos aceitos: `diagnosis`, `resolution`, `questions`, `flowchart`; versões: `v1`, `v2`.

## POST /experiments

Envia os mesmos campos do POST /runs (a versão informada é ignorada); gera v1 e v2 sequencialmente e retorna `runs` com resultados completos e status de cache. As rubricas são aplicadas **depois**, pelo avaliador.

## PUT /runs/{id}/evaluation

```json
{
  "clarity": {"score":4,"justification":"A resposta apresenta uma ordem legível e evita ambiguidade."},
  "customer_fit": {"score":3,"justification":"Alguns termos não foram explicados para o perfil leigo."},
  "actionability": {"score":4,"justification":"Existe uma verificação concreta para o próximo passo."}
}
```

## POST /comparisons

```json
{"generation_ids":[1,2]}
```

Ambas as execuções devem conter rubrica completa e ter `scenario_key` igual e versões distintas. Resposta contém `id`, `timestamp`, `generation_ids`, `summary` (médias e diferença), `results` (as duas saídas e avaliações). Este JSON também é salvo em `instance/history/comparison_ID.json`.

## GET /comparisons/{id}/export

Retorna arquivo de comparação como anexo JSON.

## Exemplo de chamada PowerShell

```powershell
$body = @{customer_id='c1'; ticket='O portal não abre'; content_type='diagnosis'; prompt_version='v2'} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/v1/runs' -Method Post -ContentType 'application/json' -Body $body
```

Em produção com token:

```powershell
$headers = @{'X-Access-Token'='TOKEN_DE_ACESSO_DA_APP'}
Invoke-RestMethod -Uri 'https://SEU_SITE.onrender.com/api/v1/profiles' -Headers $headers
```

## Códigos

- `200`: consulta, cache ou atualização bem-sucedida.
- `201`: nova execução persistida.
- `400`: entrada, rubrica, cenário ou JSON inválido.
- `401`: token da aplicação ausente ou inválido.
- `404`: registro não encontrado.
- `413`: requisição acima do limite.
- `429`: quota do provedor atingida.
- `502`: erro na comunicação/estrutura do provedor.
- `503`: configuração de credenciais inválida/ausente.
- `504`: timeout do provedor.
