from types import SimpleNamespace
from resolveai.agent import run_agent

class FakeMessages:
    def __init__(self): self.calls = 0
    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            b=SimpleNamespace(type="tool_use",name="get_ticket_triage",input={},id="tool_1")
            return SimpleNamespace(content=[b],stop_reason="tool_use")
        return SimpleNamespace(content=[SimpleNamespace(type="text",text="Triagem consultada")],stop_reason="end_turn")

def test_agent_tool_loop_with_fake_llm():
    client=SimpleNamespace(messages=FakeMessages())
    output=run_agent('T123','Meu pedido está atrasado há três horas',client,'mock-model')
    assert output['is_llm_response'] and len(output['tool_trace']) == 1
    assert output['triage']['priority']=='alta'
    assert client.messages.calls==2
