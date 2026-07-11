from __future__ import annotations

import argparse
import contextlib
import json
import sys
from typing import Any

from chatbot_eval.result_builder import error_result, exit_code_for_status


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _aggregate_exit_code(statuses: list[str]) -> int:
    if any(status == "ERROR" for status in statuses):
        return 2
    if any(status == "FAIL" for status in statuses):
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m chatbot_eval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("metrics", help="List supported metric keys.")

    metric_parser = subparsers.add_parser("metric", help="Run one metric against a golden case.")
    metric_parser.add_argument("metric_key")
    metric_parser.add_argument("test_id", nargs="?")

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one JSON payload.")
    evaluate_parser.add_argument("input_json")
    evaluate_parser.add_argument("metric_key", nargs="?")

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "metrics":
        _print_json(
            {
                "schema_version": "1.0",
                "metrics": {
                    "single_turn": [
                        "answer_correctness",
                        "reference_groundedness",
                        "unsupported_claim",
                        "negative_rejection",
                        "instruction_following",
                        "answer_relevancy",
                    ],
                    "multi_turn": [
                        "conversation_memory",
                        "context_retention",
                        "coreference_resolution",
                        "instruction_persistence",
                        "correction_handling",
                    ],
                },
            }
        )
        return 0

    if args.command == "metric":
        statuses: list[str] = []
        try:
            from chatbot_eval.metric_probe import iter_metric_probe_results

            iterator = iter(iter_metric_probe_results(args.metric_key, test_id=args.test_id))
            while True:
                try:
                    with contextlib.redirect_stdout(sys.stderr):
                        result = next(iterator)
                except StopIteration:
                    break
                _print_json(result)
                statuses.append(result["status"])
        except Exception as exc:
            result = error_result(
                error_type=exc.__class__.__name__,
                message=str(exc),
            )
            _print_json(result)
            return exit_code_for_status(result["status"])

        return _aggregate_exit_code(statuses)

    try:
        with contextlib.redirect_stdout(sys.stderr):
            if args.command == "evaluate":
                from chatbot_eval.evaluator import evaluate_file

                result = evaluate_file(args.input_json, metric_override=args.metric_key)
            else:
                result = error_result(
                    error_type="ValueError",
                    message=f"Unsupported command: {args.command}",
                )
    except Exception as exc:
        result = error_result(
            error_type=exc.__class__.__name__,
            message=str(exc),
        )

    _print_json(result)
    return exit_code_for_status(result["status"])
