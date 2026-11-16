import pytest
from resolveai.core import classify, triage, redact, POLICIES

@pytest.mark.parametrize("text,expected", [
    ("O entregador está atrasado há horas", "entrega_atrasada"),
    ("Preciso de reembolso pelo meu pedido", "reembolso"),
    ("Fizeram uma cobrança duplicada", "cobranca"),
    ("A comida chegou estragada", "qualidade_alimento"),
    ("Não consigo fazer login na minha conta", "acesso_conta"),
    ("Quero informações gerais", "outros"),
    ("Passei mal e fui ao hospital depois da refeição", "qualidade_alimento"),
    ("Quero o estorno de uma cobrança que não reconheço", "cobranca"),
])
def test_category(text, expected):
    assert classify(text)[0] == expected

def test_health_risk_requires_review():
    r = triage("T1", "Tive reação alérgica ao alimento")
    assert r["priority"] == "critica" and r["requires_human_review"]
    assert r["suggested_sla_hours"] == 1


def test_unusual_taste_routes_to_quality():
    result = triage("CH008", "Quero informar que o produto estava com gosto estranho.")
    assert result["category"] == "qualidade_alimento"
    assert result["priority"] == "media"
    assert result["requires_human_review"] is False


@pytest.mark.parametrize("text", ["Passei mal depois de consumir o pedido", "Desmaiei depois de comer"])
def test_health_signal_without_category_keyword(text):
    result = triage("RISK1", text)
    assert result["category"] == "qualidade_alimento"
    assert result["team"] == "suporte_qualidade"
    assert result["priority"] == "critica"
    assert result["requires_human_review"] is True

def test_fraud_requires_review():
    r = triage("T2", "Minha conta foi invadida ontem")
    assert r["priority"] == "alta" and r["requires_human_review"]

def test_ordinary_delay_without_review():
    r = triage("T3", "Meu pedido está atrasado poucos minutos")
    assert r["priority"] == "baixa" and not r["requires_human_review"]

def test_unknown_requires_review():
    r = triage("T4", "Preciso esclarecer uma situação diferente")
    assert r["category"] == "outros" and r["requires_human_review"]

def test_redact_email_phone_card():
    s = redact("Fale com nome@empresa.com telefone (21) 99999-9999 e cartão 1234567812345678")
    assert "nome@empresa.com" not in s and "1234567812345678" not in s

def test_policy_has_no_business_actions():
    for p in POLICIES.values():
        assert "team" in p and "reply" in p and "guidance" in p
