"""Exporta resultados reais do n8n, excluindo tokens e dados da conta local."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def export(raw_path: Path, output: Path):
    root = Path(__file__).resolve().parents[1]
    raw = raw_path.read_text(encoding="utf-8-sig")
    execution, _ = json.JSONDecoder().raw_decode(raw[raw.index("\n{") + 1:])
    assert execution["status"] == "success" and execution["finished"]
    runs = execution["data"]["resultData"]["runData"]
    nodes = []
    for name, attempts in runs.items():
        assert len(attempts) == 1
        run = attempts[0]
        assert run["executionStatus"] == "success"
        items = [item["json"] for branch in run["data"]["main"] if branch for item in branch]
        nodes.append({"name": name, "status": run["executionStatus"],
                      "execution_time_ms": run["executionTime"], "output_items": items})
    assert len(nodes) == 4
    digest = next(node["output_items"][0] for node in nodes if node["name"] == "Generate review digest")
    assert digest["total_processed"] == 4 and digest["escalated_count"] == 3
    assert digest["priority_counts"] == {"alta": 2, "critica": 1, "media": 1}
    workflow_path = root / "automation/n8n_resolveai_manual.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf8"))
    assert len(workflow["nodes"]) == 4
    http_nodes = [node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.httpRequest"]
    assert len(http_nodes) == 1
    assert http_nodes[0]["parameters"]["url"] == "http://127.0.0.1:8001/triage"
    package = next((root / ".npm-cache/_npx").glob("*/node_modules/n8n/package.json"))
    version = json.loads(package.read_text(encoding="utf8"))["version"]
    db_path = root / ".n8n-local/.n8n/database.sqlite"
    with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        stopped_at = execution["stoppedAt"].replace("T", " ").removesuffix("Z")
        row = db.execute('SELECT id, status, mode, "workflowId", "startedAt", "stoppedAt" '
                         'FROM execution_entity WHERE mode = ? AND "stoppedAt" = ? '
                         'ORDER BY id DESC LIMIT 1', (execution["mode"], stopped_at)).fetchone()
        assert row is not None, "Execução correspondente não encontrada no banco local"
        db_execution = dict(row)
    assert db_execution["status"] == "success"
    result = {
        "source": "real_n8n_execution", "n8n_version": version,
        "status": execution["status"], "finished": execution["finished"],
        "mode": execution["mode"], "started_at_utc": execution["startedAt"],
        "stopped_at_utc": execution["stoppedAt"], "database_execution": db_execution,
        "workflow_file": "automation/n8n_resolveai_manual.json",
        "workflow_sha256": hashlib.sha256(workflow_path.read_bytes()).hexdigest(),
        "nodes": nodes, "digest": digest,
        "scope": "Synthetic tickets; only HTTP destination in workflow is local FastAPI /triage."
    }
    editor_output = root / "reports/n8n_editor_digest.json"
    if editor_output.exists():
        editor_digest = json.loads(editor_output.read_text(encoding="utf8"))
        assert editor_digest == [digest], "Editor e CLI retornaram resumos diferentes"
        with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as db:
            db.row_factory = sqlite3.Row
            editor_row = db.execute('SELECT id, status, mode, "workflowId", "startedAt", "stoppedAt" '
                                    'FROM execution_entity WHERE mode = ? AND "workflowId" = ? '
                                    'ORDER BY id DESC LIMIT 1', ("manual", db_execution["workflowId"])).fetchone()
            assert editor_row is not None and editor_row["status"] == "success"
            result["editor_verification"] = {
                "database_execution": dict(editor_row), "digest_matches_cli": True,
                "output_file": "reports/n8n_editor_digest.json"
            }
        result["screenshots"] = []
        for name in ("n8n-workflow-success.jpg", "n8n-digest-output.jpg"):
            path = Path("docs/evidence") / name
            assert (root / path).is_file()
            result["screenshots"].append(path.as_posix())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"n8n_version": version, "execution": db_execution, "digest": digest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(".local-tools/n8n-execution-raw.log"))
    parser.add_argument("--output", type=Path, default=Path("reports/n8n_execution.json"))
    args = parser.parse_args()
    export(args.input, args.output)
