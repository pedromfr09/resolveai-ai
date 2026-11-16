"""Motor determinístico de triagem e roteamento, sem serviços externos.

Observação: regras demonstrativas; não são políticas oficiais do iFood.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

CATEGORIES = (
    "entrega_atrasada", "reembolso", "cobranca", "qualidade_alimento", "acesso_conta", "outros"
)
PATTERNS = {
    "entrega_atrasada": [r"atras", r"demor", r"nao chegou", r"nao entreg", r"entregador", r"pedido.*pendente", r"esperando.*pedido", r"levou.*horas?.*chegar"],
    "reembolso": [r"reembols", r"estorn", r"devolu.*dinheiro", r"dinheiro de volta", r"ressarc"],
    "cobranca": [r"cobran", r"cobr", r"cartao", r"pagamento duplicado", r"paguei duas", r"valor indevido", r"fatura", r"debito", r"compra nao autorizada"],
    "qualidade_alimento": [r"comida", r"alimento", r"refeicao", r"estragad", r"frio", r"cru", r"vencid", r"embalagem", r"alerg", r"intoxic", r"contaminad", r"hospital", r"prato", r"bebida", r"faltou.*item", r"gosto estranho"],
    "acesso_conta": [r"conta", r"senha", r"login", r"acesso", r"codigo", r"invadi", r"hackea", r"sequestr", r"nao consigo entrar", r"autenticac", r"para entrar"],
}
HEALTH_RISK = [r"alerg", r"intoxic", r"contaminad", r"hospital", r"desmaie", r"passei mal", r"corpo estranho", r"vidro na comida"]
SECURITY_RISK = [r"invadi", r"hackea", r"sequestr", r"nao reconheco", r"nao fui eu", r"fraud", r"roubaram minha conta", r"nao autorizada"]
CHARGE_RISK = [r"cobran.*duplicad", r"paguei duas", r"cobrad.*duas", r"cobranca indevida", r"valor indevido", r"pagamento duplicado", r"cobrado em duplicidade", r"cobranca duplicada", r"duas vezes"]
SEVERE_DELAY = [r"[3-9] horas?", r"(?:tres|quatro|cinco|seis|sete|oito|nove) horas?", r"mais de duas horas", r"mais de 2 horas", r"desde ontem"]

POLICIES = {
    "entrega_atrasada": {
        "team": "operacoes_entrega", "sla_hours": 4,
        "guidance": "Verificar status e histórico do pedido; não prometer prazo sem confirmação.",
        "reply": "Recebemos o relato de atraso. Vamos verificar o status do pedido antes de confirmar os próximos passos."
    },
    "reembolso": {
        "team": "suporte_financeiro", "sla_hours": 8,
        "guidance": "Checar elegibilidade conforme regras vigentes e comprovantes; não prometer estorno.",
        "reply": "Registramos sua solicitação de reembolso. A equipe vai verificar os dados e os critérios aplicáveis."
    },
    "cobranca": {
        "team": "suporte_pagamentos", "sla_hours": 4,
        "guidance": "Conferir transação em canal seguro; nunca solicitar cartão completo ou senha.",
        "reply": "Recebemos seu relato sobre uma cobrança. A equipe de pagamentos verificará a transação com segurança."
    },
    "qualidade_alimento": {
        "team": "suporte_qualidade", "sla_hours": 4,
        "guidance": "Reunir evidências e encaminhar risco à saúde imediatamente para revisão humana.",
        "reply": "Registramos seu relato sobre a qualidade do pedido. Nossa equipe fará a análise e orientará os próximos passos."
    },
    "acesso_conta": {
        "team": "seguranca_conta", "sla_hours": 2,
        "guidance": "Encaminhar suspeita de invasão para time especializado; nunca pedir senhas ou códigos.",
        "reply": "Registramos a dificuldade com a conta. Para sua segurança, a equipe responsável verificará o caso."
    },
    "outros": {
        "team": "suporte_geral", "sla_hours": 24,
        "guidance": "Pedir esclarecimentos mínimos sem dados sensíveis; encaminhar para analista.",
        "reply": "Obrigado por entrar em contato. Precisamos verificar mais informações para orientar seu atendimento."
    }
}


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _hits(text: str, patterns: list[str]) -> list[str]:
    return [pattern for pattern in patterns if re.search(pattern, text)]


def redact(text: str) -> str:
    """Redação básica para evitar exposição acidental em logs e demos; não é DLP completa."""
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[EMAIL]", text)
    text = re.sub(r"\b\+?\d{0,2}\s?\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}\b", "[TELEFONE]", text)
    text = re.sub(r"\b\d{12,19}\b", "[NUMERO_LONGO]", text)
    return text[:200]


def classify(text: str) -> tuple[str, dict[str, int]]:
    cleaned = normalize(text)
    scores = {name: len(_hits(cleaned, patterns)) for name, patterns in PATTERNS.items()}
    # O risco sanitário também define a fila quando não há outra palavra de categoria.
    if _hits(cleaned, HEALTH_RISK):
        return "qualidade_alimento", scores
    max_score = max(scores.values(), default=0)
    if not max_score:
        return "outros", scores
    # Penaliza cobranças só mencionadas em contexto de reembolso, mas mantém casos de cobrança duplicada.
    if scores["reembolso"] and scores["cobranca"] and not (_hits(cleaned, CHARGE_RISK) or "nao reconheco" in cleaned):
        scores["reembolso"] += 2
    if scores["cobranca"] and ("nao reconheco" in cleaned or _hits(cleaned, CHARGE_RISK)):
        return "cobranca", scores
    if _hits(cleaned, SECURITY_RISK) and scores["acesso_conta"]:
        return "acesso_conta", scores
    order = ("cobranca", "reembolso", "qualidade_alimento", "acesso_conta", "entrega_atrasada")
    return max(order, key=lambda c: scores[c]), scores


def triage(ticket_id: str, text: str) -> dict[str, Any]:
    """Classificação -> consulta de política -> guarda-corpos -> decisão com rastreabilidade."""
    category, scores = classify(text)
    normalized = normalize(text)
    health = bool(_hits(normalized, HEALTH_RISK))
    security = bool(_hits(normalized, SECURITY_RISK))
    charge = bool(_hits(normalized, CHARGE_RISK))
    severe_delay = category == "entrega_atrasada" and bool(_hits(normalized, SEVERE_DELAY))
    if health:
        priority, reason = "critica", "sinal_de_risco_a_saude"
    elif security or charge:
        priority, reason = "alta", "possivel_fraude_ou_seguranca_financeira"
    elif severe_delay:
        priority, reason = "alta", "atraso_prolongado"
    elif category in ("outros", "reembolso", "cobranca", "acesso_conta", "qualidade_alimento"):
        priority, reason = "media", "revisao_ou_verificacao_necessaria"
    else:
        priority, reason = "baixa", "fluxo_operacional_rotineiro"
    needs_review = priority in ("critica", "alta") or category == "outros"
    policy = POLICIES[category]
    if priority == "critica":
        sla = 1
    elif priority == "alta":
        sla = min(policy["sla_hours"], 2)
    else:
        sla = policy["sla_hours"]
    return {
        "ticket_id": ticket_id,
        "category": category,
        "priority": priority,
        "team": policy["team"],
        "requires_human_review": needs_review,
        "suggested_sla_hours": sla,
        "reason_code": reason,
        "suggested_reply_draft": policy["reply"],
        "policy_reference": {"category": category, "guidance": policy["guidance"], "source": "politicas_ficticias_demo"},
        "evidence": {"rule_scores": scores, "health_risk": health, "security_risk": security, "charge_risk": charge, "severe_delay": severe_delay},
        "redacted_excerpt": redact(text),
        "actions_executed": ["classify", "lookup_policy", "apply_risk_gates", "route"],
        "disclaimer": "DEMONSTRACAO: dados e politicas ficticias. Nao envia mensagens nem executa reembolsos."
    }
