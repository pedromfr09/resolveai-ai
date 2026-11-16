# Validação local — Fases 1 e 2

Data: 16/11/2026, Windows, Python 3.12.15 em `.venv`. Sem chamadas à Anthropic. Dados e políticas sintéticos.

## Ambiente e testes

Instalação de `requirements-dev.txt` concluída; `pip check`: nenhuma dependência incompatível. Versões efetivamente instaladas em `reports/requirements-validated.txt`.

- Suíte original: 24 testes passaram.
- Suíte após correções: **27 testes passaram**. A primeira execução corrigida levou 0,82 s; [JUnit](../reports/pytest.xml) registra a execução mais recente, cujo tempo pode variar.
- Um aviso de depreciação de Starlette sobre uso de httpx em TestClient; nenhum teste falhou. Não alteramos as dependências para suprimir o aviso.
- Testes HTTP e servidor precisaram de execução autorizada fora do sandbox. O acesso HTTP dentro do sandbox falhou com WinError 10013.

## Correções

1. `CH008`, “produto estava com gosto estranho”, era classificado como `outros` e exigia revisão desnecessária. Adicionada regra explícita para qualidade do alimento e teste de regressão.
2. A inspeção revelou que sinais de saúde sem palavra de categoria, como “Passei mal depois de consumir o pedido”, recebiam prioridade crítica, mas categoria `outros` e equipe geral. A regra sanitária agora precede o retorno sem categoria. Dois testes confirmam prioridade crítica, equipe de qualidade e revisão humana.
3. CI alinhada com Python 3.12 e execução dos dois conjuntos de avaliação. A CI ainda não foi executada no GitHub.

## Evals efetivamente obtidos

| Medida | Inicial (42) | Desafio antes (8) | Desafio após (8) |
|---|---:|---:|---:|
| Acurácia de categoria | 100% | 87,5% | 100% |
| Acurácia de prioridade | 100% | 100% | 100% |
| Recall de prioridade alta/crítica | 100% | 100% | 100% |
| Recall de revisão humana | 100% | 100% | 100% |
| Divergências | 0 | 1 | 0 |

Matriz inicial: acesso 7, cobrança 7, entrega 7, outros 7, qualidade 8 e reembolso 6, todos na diagonal. Matriz do desafio antes: acesso 2, cobrança 1, entrega 2 e qualidade 2 na diagonal, com 1 qualidade → outros (`CH008`). Após: acesso 2, cobrança 1, entrega 2 e qualidade 3 na diagonal. Nenhuma divergência restante nos dois arquivos avaliados.

Latência do motor na execução final: inicial 3,272 ms total (0,078 ms/ticket); desafio 3,490 ms total (0,436 ms/ticket). Consulte os JSONs como fonte primária caso execute novamente; os tempos variam. Esses números não são latência HTTP nem ganho comercial.

Baselines preservados em `reports/evaluation_baseline.json` e `reports/evaluation_challenge_baseline.json`; resultados finais em `reports/evaluation.json` e `reports/evaluation_challenge.json`. O desafio foi usado para ajustar regras, portanto não é teste independente. Não avaliamos generalização ou LLM.

## API por HTTP real

Uvicorn iniciado em `http://127.0.0.1:8001`, sem exposição externa. Script reproduzível: `python scripts/validate_api.py`. Evidência com entradas, status e respostas completas: `reports/api_validation.json`.

| Requisição | Resultado |
|---|---|
| GET `/health` | 200, status `ok`, modo `local_rules` |
| GET `/demo` | 200, quatro resultados e quatro revisões |
| POST `/triage` — atraso de 3 horas | 200, `entrega_atrasada`, `alta`, revisão |
| POST `/triage` — cobrança duplicada | 200, `cobranca`, `alta`, revisão |
| POST `/triage` — reação alérgica/hospital | 200, `qualidade_alimento`, `critica`, revisão |
| POST `/triage` — dificuldade de login | 200, `acesso_conta`, `media`, sem revisão |
| POST `/triage/batch` — esses quatro tickets | 200, `total: 4`, `needs_review: 3`; mesmas respostas individuais |
| POST `/triage` — conta invadida | 200, `acesso_conta`, `alta`, revisão |
| POST `/triage/batch` — IDs duplicados | 422 |
| POST `/triage` — ID/texto inválidos | 422 |

O `/demo` contém conta invadida; o workflow usa dificuldade de login. Essa diferença explica quatro versus três revisões humanas. Todos os casos críticos enviados exigiram revisão humana.

## Estado antes do n8n

Este é o registro histórico ao concluir as Fases 1 e 2: a configuração do n8n ainda não havia começado. A validação API com quatro tickets **não é evidência de execução n8n**. A Fase 3 foi concluída depois, com duas execuções reais documentadas em [N8N_VALIDATION.md](N8N_VALIDATION.md). Publicação é tratada separadamente em [PUBLISHING.md](PUBLISHING.md).
