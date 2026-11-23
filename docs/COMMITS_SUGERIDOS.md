# Evolução do projeto — roteiro para commits reais

A data de referência de planejamento é **sexta-feira, 20 de novembro de 2026**, conforme a ideia inicial de cronograma. Os itens abaixo são **etapas de trabalho sugeridas**, não um histórico de ações que já ocorreram. Faça commits na data real em que você revisar, testar ou alterar os arquivos. **Não retrodate nem atribua ações que não executou.**

1. `chore: criar estrutura inicial e configuracoes locais` — revisar `.gitignore`, `.env.example`, Docker e dependências.
2. `feat: implementar perfis tickets e contratos de resposta` — validar catálogos e quatro contratos JSON.
3. `feat: adicionar geradores com prompts versionados` — ajustar v1/v2 e descrever diferenças em `PROMPT_ENGINEERING_NOTES.md`.
4. `feat: integrar provedores e cache persistente` — executar demo e confirmar cache.
5. `feat: registrar rubricas e comparacoes em json` — avaliar duas saídas e conferir exportação.
6. `feat: adicionar interface de comparacao e historico` — testar fluxo pelo navegador.
7. `test: ampliar cobertura e configurar pipeline ci` — rodar pytest e verificar Actions.
8. `docs: registrar resultados reais e instrucoes de deploy` — adicionar evidência real, revisar README e publicar.

Comandos úteis:

```powershell
git status
git add README.md docs/PROXIMOS_PASSOS.md
git commit -m "docs: revisar instrucoes de configuracao"
git log --oneline -10
```

Para mostrar domínio técnico em entrevista, prefira commits de mudanças que você entenda e consiga explicar, por menores que sejam.
