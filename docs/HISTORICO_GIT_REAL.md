# Histórico Git local incluído no ZIP

O repositório contém a pasta oculta `.git/` e uma branch `main`. Os commits abaixo foram **criados de verdade em 23/11/2026, durante a preparação deste pacote**. Não são commits antigos do candidato e **não foram publicados no GitHub**. A autoria técnica inicial é `SupportDesk Package Setup <setup@supportdesk.local>`.

## Commits registrados antes deste documento

| Hash curto | Data (UTC) | Mensagem | Mudança real |
|---|---|---|---|
| `75820d0` | 2026-11-23 19:14 | `chore: importar projeto existente e correção de exportação no Windows` | Importação dos arquivos do ZIP corrigido já existente |
| `c3a6f04` | 2026-11-23 19:14 | `fix: alinhar Docker e exemplos de ambiente com a aplicação Flask` | Dockerfile e exemplos de variáveis revisados |
| `fa6be18` | 2026-11-23 19:15 | `test: verificar segredos, Docker e amostras antes da publicação` | Scripts de verificação de entrega e estrutura |
| `7539ffa` | 2026-11-23 19:15 | `docs: orientar publicação GitHub e registrar pendências reais` | Guia de GitHub, changelog e documentação revisada |

**Observação:** este documento e o PDF atualizado serão incluídos em um commit posterior aos listados. O `git log` é a fonte completa e definitiva, inclusive para esse último commit. Hashes e horários não foram inventados: podem ser conferidos com `git show HASH`.

## Como ver o histórico completo

```powershell
git log --oneline --decorate --all
git log --date=iso --pretty=format:"%h | %ad | %an | %s"
git show --stat HEAD
```

Para visualizar os commits na sua conta do GitHub, você precisa criar um repositório remoto vazio e fazer `git push -u origin main`. Veja `docs/GIT_E_GITHUB.md`. Após revisar e modificar o projeto, crie seus próprios commits com sua identidade real; não reescreva a autoria ou a data dos commits iniciais.
