# Auditoria pré-publicação

Preparação em 16/11/2026 para `pedromfr09/resolveai-ai`, branch `main`. Este documento registra a preparação local; não afirma que houve push ou deploy público.

## Evidências verificadas

- **27 testes automatizados**, incluindo FastAPI, regras de risco e ciclo Claude com cliente simulado. O [JUnit](../reports/pytest.xml) registra a última execução.
- **42/42** categorias no [conjunto inicial](../reports/evaluation.json) e **8/8** no [desafio](../reports/evaluation_challenge.json). Matrizes totalmente na diagonal, sem divergências atuais.
- O [baseline do desafio](../reports/evaluation_challenge_baseline.json) conserva **7/8** e o erro `CH008`. O desafio orientou a correção; não é validação independente. Ambos os conjuntos são sintéticos, sem evidência de generalização ou resultado comercial.
- n8n **2.48.4**, execuções reais **1 (CLI)** e **2 (editor)**: quatro tickets e três revisões humanas em cada uma. O registro bruto local, metadados do banco e hash do workflow foram confrontados com a [evidência sanitizada](../reports/n8n_execution.json). Os quatro resultados HTTP são compatíveis com o motor atual e com a [validação da API](../reports/api_validation.json).
- O motor principal é determinístico. Claude é opcional e não foi validado com chamadas reais neste projeto; o teste simulado não equivale a validação Anthropic.
- A versão preparada para publicação passou novamente nos **27 testes**, com um aviso de depreciação já conhecido; `pip check` não encontrou incompatibilidades. No navegador, filtro de conta e seleção de ticket atualizaram a decisão corretamente, sem erros de console. [Captura da demo estática](evidence/static-demo.jpg).

## Conteúdo para publicação

Código, testes, datasets sintéticos, dois workflows importáveis, documentação, relatórios sanitizados e capturas do n8n. O `index.html` está na raiz e contém snapshots embutidos, sem dependências de serviços locais. A configuração solicitada para Pages é `main` e `/(root)`; veja [PUBLISHING.md](PUBLISHING.md).

`.gitignore` exclui ambiente virtual, arquivos `.env` reais, ferramentas/cache locais, banco e configuração do n8n, dependências, chaves e logs. `.env.example` contém somente nomes de variáveis e valores vazios. As capturas mostram tickets sintéticos e resultados, sem conta ou senha. A autoria Git local usa endereço `noreply` da conta GitHub.

A lista preparada contém **44 arquivos**. `git diff --check` e `git diff --cached --check` passaram. A inspeção dos arquivos preparados não encontrou os formatos procurados de chaves Anthropic/GitHub, chaves privadas, tokens internos n8n, hostname no JUnit ou caminhos pessoais absolutos. As exclusões de ambiente, banco, configuração n8n, caches e logs foram confirmadas com `git check-ignore`. Essa verificação não equivale a uma auditoria de segurança do produto ou de suas dependências.

O primeiro push público depende de aprovação explícita do proprietário. A configuração de Pages e a verificação dos links públicos devem ocorrer após esse push. A CLI `gh` não foi localizada; o conector confirmou a conta `pedromfr09`, mas não oferece criação de repositório. O roteiro manual de criação vazia e ativação de Pages está em [PUBLISHING.md](PUBLISHING.md).
