from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_CASES = [
    ("QB-ST-001", "answer_correctness"),
    ("QB-ST-002", "reference_groundedness"),
    ("QB-ST-003", "unsupported_claim"),
    ("QB-ST-004", "negative_rejection"),
    ("QB-ST-005", "instruction_following"),
    ("QB-ST-006", "answer_relevancy"),
    ("QB-MT-001", "conversation_memory"),
    ("QB-MT-002", "correction_handling"),
    ("QB-MT-003", "context_retention"),
    ("QB-MT-004", "coreference_resolution"),
    ("QB-MT-005", "instruction_persistence"),
]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        value = json.load(file)
    return value if isinstance(value, dict) else None


def _metric_detail(result: dict[str, Any] | None, expected_metric: str) -> dict[str, Any] | None:
    if not result:
        return None
    for item in result.get("metrics") or []:
        if item.get("key") == expected_metric:
            return item
    metrics = result.get("metrics") or []
    return metrics[0] if metrics else None


def _text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def _case_row(artifact_root: Path, test_id: str, expected_metric: str) -> dict[str, str]:
    case_dir = artifact_root / test_id
    result = _read_json(case_dir / "evaluation_result.json")
    metric = _metric_detail(result, expected_metric)
    status = result.get("status", "MISSING") if result else "MISSING"

    score = ""
    threshold = ""
    detail = ""
    if metric:
        if metric.get("score") is not None:
            score = f"{metric['score']:.3f}" if isinstance(metric.get("score"), float) else str(metric.get("score"))
        if metric.get("threshold") is not None:
            threshold = f"{metric['threshold']:.3f}" if isinstance(metric.get("threshold"), float) else str(metric.get("threshold"))
        detail = metric.get("error") or metric.get("reason") or ""
    elif result and result.get("error"):
        error = result["error"]
        detail = f"{error.get('type', 'Error')}: {error.get('message', '')}"

    return {
        "test_id": test_id,
        "metric": expected_metric,
        "status": status,
        "score": score,
        "threshold": threshold,
        "detail": _text(detail),
        "artifact": _text(str(case_dir)),
    }


def build_report(artifact_root: Path, config_name: str) -> str:
    rows = [_case_row(artifact_root, test_id, metric) for test_id, metric in EXPECTED_CASES]
    counts = Counter(row["status"] for row in rows)
    generated_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# QuillBot Evaluation Report",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Chatbot config: `{config_name}`",
        f"- Artifact root: `{artifact_root}`",
        f"- Total cases: `{len(rows)}`",
        f"- PASS: `{counts.get('PASS', 0)}`",
        f"- FAIL: `{counts.get('FAIL', 0)}`",
        f"- ERROR: `{counts.get('ERROR', 0)}`",
        f"- MISSING: `{counts.get('MISSING', 0)}`",
        "",
        "## Metric Summary",
        "",
        "| Metric | Test ID | Status | Score | Threshold |",
        "|---|---:|---:|---:|---:|",
    ]

    for row in rows:
        lines.append(
            f"| `{row['metric']}` | `{row['test_id']}` | `{row['status']}` | "
            f"{row['score']} | {row['threshold']} |"
        )

    problem_rows = [row for row in rows if row["status"] != "PASS"]
    lines.extend(["", "## Failures, Errors, and Missing Cases", ""])
    if not problem_rows:
        lines.append("All expected QuillBot metric cases passed.")
    else:
        lines.extend([
            "| Test ID | Metric | Status | Detail | Artifact |",
            "|---|---|---:|---|---|",
        ])
        for row in problem_rows:
            lines.append(
                f"| `{row['test_id']}` | `{row['metric']}` | `{row['status']}` | "
                f"{row['detail']} | `{row['artifact']}` |"
            )

    lines.extend(["", "## Artifact Index", "", "| Test ID | Artifact Directory |", "|---|---|"])
    for row in rows:
        lines.append(f"| `{row['test_id']}` | `{row['artifact']}` |")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown report from QuillBot DeepEval artifacts.")
    parser.add_argument(
        "--artifacts",
        default="java-automation/target/deepeval-artifacts",
        help="Directory containing per-test DeepEval artifact folders.",
    )
    parser.add_argument(
        "--output",
        default="reports/quillbot-evaluation-report.md",
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--config-name",
        default="config/quillbot.properties",
        help="Chatbot config name to display in the report.",
    )
    args = parser.parse_args()

    artifact_root = Path(args.artifacts).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(artifact_root, args.config_name), encoding="utf-8")
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())