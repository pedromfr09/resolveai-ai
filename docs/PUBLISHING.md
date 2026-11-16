# Publicação do ResolveAI

Destino planejado: `pedromfr09/resolveai-ai`, repositório público, branch `main`. A preparação local não comprova publicação; primeiro push depende da aprovação do proprietário.

## Criar o repositório vazio

GitHub CLI não foi encontrado neste ambiente. A conta conectada pelo conector é `pedromfr09`, mas o conector disponível não possui comando de criação de repositório.

1. Entre em [github.com/new](https://github.com/new).
2. Em **Owner**, escolha **pedromfr09**; em **Repository name**, escreva **resolveai-ai**.
3. Descrição sugerida: `Triagem auditável com FastAPI, regras determinísticas, evals sintéticos e automação n8n validada.`
4. Selecione **Public**. Deixe desmarcada a criação de README, `.gitignore` e licença, pois os arquivos locais serão enviados no primeiro push.
5. Clique **Create repository**. A criação vazia não envia o projeto local.

Após a aprovação explícita do primeiro push, envie a branch local `main` para `https://github.com/pedromfr09/resolveai-ai.git`. Autenticação Git pode exigir que o proprietário entre na conta; não inclua tokens na URL nem em arquivos.

## Ativar GitHub Pages

Depois que `main` estiver publicada:

1. No repositório, clique **Settings → Pages**.
2. Em **Build and deployment → Source**, escolha **Deploy from a branch**.
3. Em **Branch**, selecione **main**; na pasta, escolha **/(root)**.
4. Clique **Save** e acompanhe o deploy na aba **Actions**.
5. Abra a URL informada pelo GitHub. Endereço esperado, somente após deploy bem-sucedido: `https://pedromfr09.github.io/resolveai-ai/`.

O `index.html` está na raiz e usa CSS, JavaScript e snapshots embutidos, sem requisições à FastAPI, n8n, CDN ou LLM. O arquivo `.nojekyll` permite servir os arquivos estáticos sem processamento Jekyll. Pages **não executa API ou workflow n8n**.

## Conteúdo e evidências

Publicar código, testes, dados sintéticos, workflows importáveis, README, documentos e evidências sanitizadas. Não publicar `.venv`, `.env`, `.local-tools`, `.npm-cache`, `.n8n-local`, bancos, logs privados ou arquivos temporários. A pasta n8n contém dados da conta e chaves; o log bruto da CLI contém tokens internos. Esses arquivos permanecem somente na máquina, ignorados pelo Git.

Confira [API/testes/evals](PHASE1_2_VALIDATION.md), [execução n8n](N8N_VALIDATION.md) e [relatório pré-publicação](PREPUBLICATION.md). A avaliação é sintética; o desafio orientou ajustes, sem teste independente. Claude não foi validado com chamadas reais neste projeto.

Referência: [configurar a origem de publicação no GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
