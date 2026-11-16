# Publicação do ResolveAI

**Status em 16/11/2026:** repositório público publicado em [pedromfr09/resolveai-ai](https://github.com/pedromfr09/resolveai-ai), branch `main`, commit inicial [`a1025b1`](https://github.com/pedromfr09/resolveai-ai/commit/a1025b17ccefb8391bc2e1f5edf8b075741c2689). A [suíte CI](https://github.com/pedromfr09/resolveai-ai/actions/runs/43981829098) concluiu com sucesso.

## GitHub Pages — publicação concluída

**O GitHub confirmou o deploy bem-sucedido** na branch `main`: [execução Pages](https://github.com/pedromfr09/resolveai-ai/actions/runs/43982444681).

**[Abrir demonstração pública](https://pedromfr09.github.io/resolveai-ai/)**. Conferir manualmente no navegador o carregamento e os controles interativos; o deploy bem-sucedido não substitui um teste visual da página.

O arquivo `index.html` está na raiz e contém CSS, JavaScript e exemplos de triagem pré-calculados, sem chamadas à FastAPI, n8n, CDN ou LLM. O `.nojekyll` impede processamento Jekyll. **Pages não executa a API nem o workflow n8n.**

## O que foi publicado

Código, testes, datasets sintéticos, dois workflows n8n importáveis, README, documentos, resultados sanitizados e capturas. Os registros brutos, `.venv`, `.env`, `.local-tools`, `.npm-cache`, `.n8n-local`, bancos e arquivos privados continuam fora do Git.

Evidências: [API, testes e evals](PHASE1_2_VALIDATION.md), [execução n8n](N8N_VALIDATION.md), [auditoria pré-publicação](PREPUBLICATION.md). As avaliações utilizam dados sintéticos; o desafio orientou correções e não é teste independente. A integração real com Claude **não** foi validada neste projeto.

Configuração de Pages: [documentação oficial do GitHub](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
