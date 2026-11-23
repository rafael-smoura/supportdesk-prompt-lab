# Correção de exportação no Windows

## Sintoma

O teste `test_rubric_and_comparison_persist` falhava com `PermissionError: [WinError 5]` na segunda exportação de `comparison_1.json`.

## Causa

A rota de download usava `send_file(path)`. A resposta de teste podia manter o arquivo original aberto no Windows, bloqueando a substituição atômica feita por `os.replace()` ao atualizar o JSON existente.

## Correção

A rota agora lê os bytes com `path.read_bytes()` e passa `BytesIO(...)` ao `send_file`. O arquivo físico é fechado antes de a resposta ser transmitida. O serviço de exportação preserva a escrita atômica no disco.

## Verificação

Execute na raiz do projeto, com o ambiente virtual ativo:

```powershell
python -m pytest -q
python run.py
```

Espera-se que a suíte de testes finalize sem falhas. A integração Flask não foi executada no ambiente de montagem deste pacote, porque as dependências Flask/Flask-SQLAlchemy não estão disponíveis nele. O teste de regressão está em `tests/test_api.py`.
