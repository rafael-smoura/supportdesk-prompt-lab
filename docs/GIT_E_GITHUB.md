# Git e GitHub — guia para publicar este projeto

## O que existe neste ZIP

Este pacote contém um repositório Git local de verdade: a pasta oculta `.git/`, a branch `main` e commits realizados **durante a preparação desta versão**. Não existe repositório remoto vinculado nem commits feitos na conta do candidato. O autor técnico dos commits iniciais é `SupportDesk Package Setup <setup@supportdesk.local>`; eles não devem ser apresentados como trabalho realizado pelo candidato em datas anteriores.

A referência a **20/11/2026** em roteiros anteriores é uma data de planejamento, **não** uma data de commits. As datas dos commits são as que o Git registrou quando as alterações foram feitas. Para verificar, execute:

```powershell
git status
git log --date=iso --pretty=format:"%h | %ad | %an | %s"
git branch --show-current
```

**Atenção:** extrair um ZIP com a opção de não incluir arquivos ocultos pode eliminar `.git/`. Confirme `Test-Path .git` no PowerShell. Se o resultado for `False`, extraia o ZIP novamente preservando arquivos ocultos; não rode `git init` por cima sem verificar.

## 1. Preparar sua identidade para os próximos commits

No terminal, dentro da pasta do projeto:

```powershell
git config --local user.name "SEU NOME"
git config --local user.email "EMAIL_CONFIRMADO_NO_GITHUB"
git config --local --get user.name
git config --local --get user.email
```

Isso altera a autoria **dos próximos commits**, não reescreve o histórico importado. Utilize o e-mail associado à sua conta ou o endereço privado `noreply` oferecido pelo GitHub. Não publique dados pessoais que não deseja divulgar.

## 2. Validar antes de publicar

```powershell
python -m pytest -q
python scripts/verify_structure.py
python scripts/preflight.py
git status
git check-ignore .env
git check-ignore .venv
```

`git check-ignore` deve indicar `.env` e `.venv`. `git status` não deve mostrar segredos, banco SQLite ou arquivos de `instance/history/`. Se tiver uma chave real em `.env`, **não use `git add -f .env`**.

## 3. Criar o repositório remoto

1. Acesse https://github.com/new e crie um repositório, por exemplo `supportdesk-prompt-lab`.
2. Escolha um repositório **vazio**, sem gerar README, `.gitignore` ou licença no site (esses arquivos já existem localmente).
3. Copie a URL HTTPS do repositório criado.
4. No PowerShell, rode:

```powershell
git remote -v
git remote add origin https://github.com/SEU_USUARIO/supportdesk-prompt-lab.git
git push -u origin main
```

Se `origin` já existir, verifique a URL com `git remote -v`. Para corrigir uma URL equivocada: `git remote set-url origin URL_CORRETA`. **Não sobrescreva um remoto existente sem conferir o conteúdo.**

O GitHub poderá solicitar autenticação pelo navegador ou gerenciador de credenciais. Não coloque senha nem token em comandos que serão compartilhados.

## 4. Fazer commits próprios e verificáveis

O histórico inicial acompanha o pacote. A partir daqui, faça mudanças reais, execute os testes e registre o que alterou. Exemplo de sequência:

```powershell
# Após configurar e validar sua integração real, adicionar a evidência revisada:
git add samples/comparacao_real_analisada.json docs/RESULTADO_DO_EXPERIMENTO.md
git commit -m "docs: registrar comparacao real entre prompts v1 e v2"
git push
```

Não é necessário fazer `git add .` sem revisar. Para conferir o que vai entrar:

```powershell
git status --short
git diff --cached
git log --oneline --decorate -10
```

**Não retrodate commits nem reescreva a autoria para sugerir trabalho anterior.** O desafio permite ferramentas de apoio, mas a defesa técnica exige que você compreenda e consiga modificar a solução.

## 5. Confirmar CI e preparar entrega

- Abra a aba **Actions** do repositório. O workflow `.github/workflows/ci.yml` deve executar os testes no push.
- Se o CI falhar, abra o log e corrija o problema; não marque como concluído sem executar novamente.
- Confirme no GitHub que `.env`, `.venv`, `instance/history/` e banco local não aparecem entre os arquivos.
- Antes de enviar o desafio, execute `python scripts/preflight.py --strict`: o modo estrito exige a amostra de comparação com IA real.
- O deploy é opcional. Veja `docs/PROXIMOS_PASSOS.md` para Render e Docker.

## Se você já tem um repositório Git com commits próprios

**Não substitua nem sobrescreva seu histórico existente** por este `.git`. Nesse caso, copie apenas os arquivos de código/documentação que deseja incorporar para seu repositório, compare as mudanças e faça seus próprios commits. O histórico local do ZIP serve como referência técnica, não como substituto do seu histórico.
