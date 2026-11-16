from pathlib import Path
from scripts.evaluate import evaluate

def test_evaluation_is_reproducible():
    p=Path(__file__).resolve().parents[1]/'data'/'tickets_labeled.jsonl'
    result=evaluate(p)
    assert result['sample_size']>=30
    assert 0<=result['category_accuracy']<=1
    assert result['human_review_recall'] is not None
