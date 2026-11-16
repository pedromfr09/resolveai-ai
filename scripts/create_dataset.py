"""Conjunto pequeno e sintético, anotado manualmente para validação de regressão.
Gerar exemplos é etapa preparatória; o avaliador NÃO utiliza as classes esperadas na predição.
"""
import json
from pathlib import Path

# (texto, categoria, prioridade, requer revisão humana)
CASES = [
 ("Meu pedido está atrasado vinte minutos", "entrega_atrasada", "baixa", False),
 ("Entregador ainda não chegou com o pedido", "entrega_atrasada", "baixa", False),
 ("A entrega demorou mais do que o combinado", "entrega_atrasada", "baixa", False),
 ("Estou esperando meu pedido desde ontem", "entrega_atrasada", "alta", True),
 ("O pedido está atrasado há 3 horas", "entrega_atrasada", "alta", True),
 ("Minha entrega está atrasada desde o almoço", "entrega_atrasada", "baixa", False),
 ("O pedido aparece pendente e não foi entregue", "entrega_atrasada", "baixa", False),
 ("Gostaria de solicitar reembolso do valor pago", "reembolso", "media", False),
 ("Quando vou receber meu estorno?", "reembolso", "media", False),
 ("Quero meu dinheiro de volta pelo pedido", "reembolso", "media", False),
 ("Preciso do reembolso da compra cancelada", "reembolso", "media", False),
 ("Qual é o andamento da devolução do dinheiro?", "reembolso", "media", False),
 ("Solicitei estorno e ainda não obtive resposta", "reembolso", "media", False),
 ("O aplicativo registrou uma cobrança duplicada", "cobranca", "alta", True),
 ("Paguei duas vezes pelo mesmo pedido", "cobranca", "alta", True),
 ("Há um valor indevido na minha fatura", "cobranca", "alta", True),
 ("Meu cartão foi cobrado em duplicidade", "cobranca", "alta", True),
 ("Existe cobrança indevida na compra", "cobranca", "alta", True),
 ("Não reconheço uma cobrança na fatura", "cobranca", "alta", True),
 ("Gostaria de consultar a cobrança da taxa", "cobranca", "media", False),
 ("A comida chegou completamente fria", "qualidade_alimento", "media", False),
 ("A refeição estava estragada", "qualidade_alimento", "media", False),
 ("O alimento veio cru", "qualidade_alimento", "media", False),
 ("A embalagem estava aberta e a comida derramada", "qualidade_alimento", "media", False),
 ("Tive reação alérgica após comer o pedido", "qualidade_alimento", "critica", True),
 ("Fui ao hospital com intoxicação depois da refeição", "qualidade_alimento", "critica", True),
 ("Encontrei vidro na comida", "qualidade_alimento", "critica", True),
 ("O alimento chegou contaminado", "qualidade_alimento", "critica", True),
 ("Não consigo acessar minha conta", "acesso_conta", "media", False),
 ("Esqueci a senha e não consigo entrar", "acesso_conta", "media", False),
 ("O login está bloqueado", "acesso_conta", "media", False),
 ("Minha conta foi invadida", "acesso_conta", "alta", True),
 ("Hackearam minha conta e trocaram o acesso", "acesso_conta", "alta", True),
 ("Não reconheço o acesso registrado na conta", "acesso_conta", "alta", True),
 ("Quero mudar a senha da conta", "acesso_conta", "media", False),
 ("Qual o horário de atendimento do suporte?", "outros", "media", True),
 ("Gostaria de esclarecer uma dúvida sobre o aplicativo", "outros", "media", True),
 ("Tenho uma sugestão para a interface", "outros", "media", True),
 ("Onde encontro o termo de uso?", "outros", "media", True),
 ("Quero falar sobre uma funcionalidade nova", "outros", "media", True),
 ("Preciso de orientação sobre algo diferente", "outros", "media", True),
 ("Gostaria de enviar um elogio ao suporte", "outros", "media", True),
]

if __name__ == '__main__':
    target=Path(__file__).resolve().parents[1]/'data'/'tickets_labeled.jsonl'
    with target.open('w',encoding='utf8') as f:
        for i,(text,cat,priority,review) in enumerate(CASES,1):
            f.write(json.dumps({'ticket_id':f'SYN{i:03}', 'text':text, 'expected_category':cat,'expected_priority':priority,'requires_human_review':review},ensure_ascii=False)+'\n')
    print(len(CASES),target)
