from fastapi.testclient import TestClient
from resolveai.api import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_demo():
    assert len(client.get('/demo').json()['results']) == 4

def test_policy():
    assert client.get('/policies').status_code == 200

def test_triage():
    r=client.post('/triage', json={'ticket_id': 'ABC12', 'text': 'Quero reembolso do meu pedido'})
    assert r.status_code == 200 and r.json()['category'] == 'reembolso'

def test_batch():
    r=client.post('/triage/batch',json={'tickets':[{'ticket_id':'A1','text':'Minha conta foi invadida'}, {'ticket_id':'A2','text':'Minha entrega está atrasada'}]})
    assert r.status_code == 200 and r.json()['total'] == 2

def test_duplicate_ticket():
    r=client.post('/triage/batch',json={'tickets':[{'ticket_id':'A1','text':'Minha conta foi invadida'}, {'ticket_id':'A1','text':'Minha entrega está atrasada'}]})
    assert r.status_code == 422

def test_invalid_text_and_id():
    assert client.post('/triage',json={'ticket_id': 'wrong id', 'text': 'Oi'}).status_code == 422

def test_llm_off_by_default(monkeypatch):
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    monkeypatch.delenv('ANTHROPIC_MODEL', raising=False)
    assert client.post('/agent/claude',json={'ticket_id':'A1','text':'Minha conta foi invadida'}).status_code == 503
