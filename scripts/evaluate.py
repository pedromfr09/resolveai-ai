"""Eval reproduzível, sem credencial externa ou dados reais."""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from resolveai.core import triage


def evaluate(dataset: Path):
    records = [json.loads(line) for line in dataset.read_text(encoding="utf8").splitlines() if line.strip()]
    start = time.perf_counter()
    predictions = [triage(item["ticket_id"], item["text"]) for item in records]
    elapsed = (time.perf_counter() - start) * 1000
    n = len(records)
    correct = sum(pred["category"] == item["expected_category"] for item, pred in zip(records, predictions))
    critical = [i for i, item in enumerate(records) if item["expected_priority"] in ("alta", "critica")]
    review = [i for i, item in enumerate(records) if item["requires_human_review"]]
    matrix = Counter((item["expected_category"], pred["category"]) for item, pred in zip(records, predictions))
    errors = [dict(ticket_id=item["ticket_id"], expected_category=item["expected_category"], predicted_category=pred["category"], expected_priority=item["expected_priority"], predicted_priority=pred["priority"], expected_review=item["requires_human_review"], predicted_review=pred["requires_human_review"])
              for item, pred in zip(records, predictions) if (pred["category"] != item["expected_category"] or pred["priority"] != item["expected_priority"] or pred["requires_human_review"] != item["requires_human_review"])]
    return {
      "dataset": str(dataset.name), "source": "curated_synthetic_examples", "sample_size": n,
      "category_accuracy": round(correct / n, 4),
      "priority_accuracy": round(sum(p["priority"] == r["expected_priority"] for p,r in zip(predictions, records)) / n, 4),
      "high_priority_recall": round(sum(predictions[i]["priority"] in ("alta", "critica") for i in critical) / len(critical), 4) if critical else None,
      "human_review_recall": round(sum(predictions[i]["requires_human_review"] for i in review) / len(review), 4) if review else None,
      "elapsed_ms_total": round(elapsed, 3), "mean_ms_per_ticket": round(elapsed / n, 3),
      "confusion_matrix": [{"expected": a, "predicted": b, "count": count} for (a,b),count in sorted(matrix.items())],
      "mismatches": errors, "caveat": "Métricas locais em dados sintéticos construídos para validar o MVP. Não representam performance em produção, nem avaliação da LLM."
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "tickets_labeled.jsonl")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.data)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf8")
