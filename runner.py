from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from deepeval.test_case import ConversationalTestCase, LLMTestCase, Turn

from chatbot_client import call_chatbot
from chatbot_multiturn_client import call_chatbot_multiturn
from dataset import ROOT_DIR, load_multi_turn_dataset, load_single_turn_dataset
from deepeval_runner import EvaluationResult, evaluate_metrics
from metrics.metric_sets import build_single_turn_metrics
from metrics.multiturn.metric_sets import build_multiturn_metrics


REPORTS_DIR = ROOT_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "evaluation_results.json"


def run_single_turn_item(item: dict[str, Any]) -> EvaluationResult:
    test_id = item["test_id"]
    try:
        actual_output = call_chatbot(
            item["input"],
            reference_context=item.get("reference_context"),
        )
        test_case = LLMTestCase(
            input=item["input"],
            actual_output=actual_output,
            expected_output=item.get("expected_output"),
            retrieval_context=[item.get("reference_context", "")],
        )
        metrics = build_single_turn_metrics(item.get("expected_behavior", "answer"))
        status, metric_results = evaluate_metrics(test_case, metrics)
        return EvaluationResult(
            test_id=test_id,
            suite="single",
            status=status,
            metrics=metric_results,
            input=item["input"],
            actual_output=actual_output,
        )
    except Exception as exc:
        return EvaluationResult(
            test_id=test_id,
            suite="single",
            status="ERROR",
            input=item.get("input"),
            error=f"{exc.__class__.__name__}: {exc}",
        )


def run_multi_turn_item(item: dict[str, Any]) -> EvaluationResult:
    test_id = item["test_id"]
    conversation_history: list[dict[str, str]] = []
    deepeval_turns: list[Turn] = []
    assistant_turns: list[str] = []

    try:
        for user_message in item["user_turns"]:
            deepeval_turns.append(Turn(role="user", content=user_message))
            assistant_message = call_chatbot_multiturn(
                user_message,
                conversation_history=conversation_history,
                reference_context=item.get("reference_context"),
            )
            assistant_turns.append(assistant_message)
            deepeval_turns.append(Turn(role="assistant", content=assistant_message))
            conversation_history.extend(
                [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_message},
                ]
            )

        test_case = ConversationalTestCase(
            scenario=item.get("scenario"),
            expected_outcome=item.get("expected_outcome"),
            chatbot_role=item.get("chatbot_role", "Yardımcı asistan."),
            turns=deepeval_turns,
        )
        metrics = build_multiturn_metrics(metric_focus=item.get("metric_focus"))
        status, metric_results = evaluate_metrics(test_case, metrics)
        return EvaluationResult(
            test_id=test_id,
            suite="multi",
            status=status,
            metrics=metric_results,
            user_turns=item.get("user_turns", []),
            assistant_turns=assistant_turns,
            metric_focus=item.get("metric_focus"),
        )
    except Exception as exc:
        return EvaluationResult(
            test_id=test_id,
            suite="multi",
            status="ERROR",
            user_turns=item.get("user_turns", []),
            assistant_turns=assistant_turns,
            metric_focus=item.get("metric_focus"),
            error=f"{exc.__class__.__name__}: {exc}",
        )


def print_result(result: EvaluationResult) -> None:
    focus = f" {result.metric_focus}" if result.metric_focus else ""
    print(f"[{result.test_id}]{focus}")

    if result.suite == "multi" and result.user_turns is not None:
        print(f"User turns: {len(result.user_turns)}")

    print(f"Result: {result.status}")

    failed_or_error_metrics = [m for m in result.metrics if m.status != "PASS"]
    for metric in failed_or_error_metrics:
        print(f"Failed metric: {metric.name}")
        if metric.score is not None:
            print(f"Score: {metric.score:.2f}")
        if metric.threshold is not None:
            print(f"Threshold: {metric.threshold:.2f}")
        if metric.reason:
            print(f"Reason: {metric.reason}")
        if metric.error:
            print(f"Error: {metric.error}")

    if result.error:
        print(f"Error: {result.error}")

    print()


def print_section(title: str) -> None:
    print("=" * 50)
    print(title)
    print("=" * 50)
    print()


def summarize(results: list[EvaluationResult]) -> dict[str, int]:
    return {
        "total": len(results),
        "pass": sum(result.status == "PASS" for result in results),
        "fail": sum(result.status == "FAIL" for result in results),
        "error": sum(result.status == "ERROR" for result in results),
    }


def write_report(results: list[EvaluationResult], path: Path = REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summarize(results),
        "results": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run black-box chatbot evaluation.")
    parser.add_argument(
        "--suite",
        choices=["single", "multi", "all"],
        default="all",
        help="Evaluation suite to run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results: list[EvaluationResult] = []

    if args.suite in {"single", "all"}:
        print_section("SINGLE-TURN EVALUATION")
        for item in load_single_turn_dataset():
            result = run_single_turn_item(item)
            results.append(result)
            print_result(result)

    if args.suite in {"multi", "all"}:
        print_section("MULTI-TURN EVALUATION")
        for item in load_multi_turn_dataset():
            result = run_multi_turn_item(item)
            results.append(result)
            print_result(result)

    summary = summarize(results)
    print_section("SUMMARY")
    print(f"Total: {summary['total']}")
    print(f"PASS: {summary['pass']}")
    print(f"FAIL: {summary['fail']}")
    print(f"ERROR: {summary['error']}")
    print("=" * 50)

    write_report(results)
    print(f"Report: {REPORT_PATH}")

    return 1 if summary["fail"] or summary["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
