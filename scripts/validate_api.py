"""Valida HTTP real contra Uvicorn; não executa n8n nem chama Claude."""
import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import httpx


def validate(base_url: str):
    tickets = [
        {"ticket_id": "DEMO-001", "text": "Meu pedido está atrasado há 3 horas"},
        {"ticket_id": "DEMO-002", "text": "Fui cobrado duas vezes pelo mesmo pedido"},
        {"ticket_id": "DEMO-003", "text": "Tive reação alérgica e fui ao hospital após comer"},
        {"ticket_id": "DEMO-004", "text": "Não consigo entrar na minha conta"},
    ]
    expected = [
        ("entrega_atrasada", "alta", True),
        ("cobranca", "alta", True),
        ("qualidade_alimento", "critica", True),
        ("acesso_conta", "media", False),
    ]
    requests = []
    with httpx.Client(base_url=base_url, timeout=10, trust_env=False) as client:
        def request(method, path, body=None, status=200):
            response = client.request(method, path, json=body)
            payload = response.json()
            requests.append({"method": method, "path": path, "request": body,
                             "status_code": response.status_code, "response": payload})
            assert response.status_code == status, (path, response.status_code, payload)
            return payload

        assert request("GET", "/health")["status"] == "ok"
        demo = request("GET", "/demo")
        assert len(demo["results"]) == 4
        assert all(row["requires_human_review"] for row in demo["results"])
        singles = []
        for ticket, (category, priority, review) in zip(tickets, expected):
            row = request("POST", "/triage", ticket)
            assert (row["category"], row["priority"], row["requires_human_review"]) == (category, priority, review)
            singles.append(row)
        batch = request("POST", "/triage/batch", {"tickets": tickets})
        assert batch["total"] == 4 and batch["needs_review"] == 3
        assert batch["results"] == singles
        invaded = request("POST", "/triage", {
            "ticket_id": "SECURITY-001", "text": "Minha conta foi invadida e não reconheço o acesso"})
        assert invaded["category"] == "acesso_conta"
        assert invaded["priority"] == "alta" and invaded["requires_human_review"]
        request("POST", "/triage/batch", {"tickets": [tickets[0], tickets[0]]}, status=422)
        request("POST", "/triage", {"ticket_id": "invalid id", "text": "Oi"}, status=422)
    return {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(), "base_url": base_url,
        "transport": "real_http", "passed": True,
        "workflow_input_api_only": {"total_processed": batch["total"], "escalated_count": batch["needs_review"]},
        "n8n_executed": False, "anthropic_called": False, "requests": requests,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8001")
    parser.add_argument("--output", type=Path, default=Path("reports/api_validation.json"))
    args = parser.parse_args()
    result = validate(args.base_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps({k: v for k, v in result.items() if k != "requests"}, indent=2))
