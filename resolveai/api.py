"""API de triagem: operacional sem chave de LLM; assistência Claude opcional."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import POLICIES, triage

app = FastAPI(title="ResolveAI - Complaint Triage", version="1.0.0", description="Demonstração independente, com dados e políticas fictícios. Não afiliada ao iFood.")

class TicketIn(BaseModel):
    ticket_id: Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]
    text: Annotated[str, Field(min_length=10, max_length=2000)]

class BatchIn(BaseModel):
    tickets: Annotated[list[TicketIn], Field(min_length=1, max_length=100)]

@app.get("/health")
def health():
    return {"status": "ok", "service": "resolveai", "mode": "local_rules"}

@app.get("/policies")
def policies():
    return {"data": POLICIES, "origin": "invented_for_demo_not_company_policy"}

@app.post("/triage")
def triage_one(ticket: TicketIn):
    return triage(ticket.ticket_id, ticket.text)

@app.post("/triage/batch")
def triage_batch(batch: BatchIn):
    ids = [t.ticket_id for t in batch.tickets]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=422, detail="ticket_id duplicado no lote")
    results = [triage(t.ticket_id, t.text) for t in batch.tickets]
    return {"total": len(results), "needs_review": sum(r["requires_human_review"] for r in results), "results": results}

@app.get("/demo")
def demo():
    cases = [
        ("T001", "O pedido está atrasado há três horas e ainda não chegou."),
        ("T002", "Fui cobrado duas vezes pelo mesmo pedido e quero orientação."),
        ("T003", "Comi o pedido e tive reação alérgica, precisei ir ao hospital."),
        ("T004", "Minha conta foi invadida e não reconheço a compra realizada."),
    ]
    return {"source": "synthetic_examples", "results": [triage(k, t) for k,t in cases]}

@app.post("/agent/claude")
def claude_agent(ticket: TicketIn):
    """Explicação conversacional com ferramentas locais; disponível somente com credenciais."""
    if not (os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_MODEL")):
        raise HTTPException(status_code=503, detail="Claude opcional desabilitado: configure ANTHROPIC_API_KEY e ANTHROPIC_MODEL")
    try:
        from anthropic import Anthropic
        from .agent import run_agent
        result = run_agent(ticket.ticket_id, ticket.text, Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]), os.environ["ANTHROPIC_MODEL"])
        return result
    except (ImportError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        # Não vazar respostas ou segredos de APIs externas para o cliente.
        raise HTTPException(status_code=502, detail="Falha na integracao externa; verifique configuracao e logs de forma privada")
