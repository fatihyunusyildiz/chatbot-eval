from __future__ import annotations

import json

from chatbot_eval import cli
from chatbot_eval import metric_probe


def _decode_json_objects(output: str) -> list[dict]:
    decoder = json.JSONDecoder()
    index = 0
    objects = []
    while index < len(output):
        while index < len(output) and output[index].isspace():
            index += 1
        if index >= len(output):
            break
        value, index = decoder.raw_decode(output, index)
        objects.append(value)
    return objects


def test_metric_cli_prints_each_case_as_separate_json(monkeypatch, capsys):
    def fake_results(metric_key, test_id=None):
        yield {
            "schema_version": "1.0",
            "test_id": "MT-001",
            "suite_type": "multi_turn",
            "status": "PASS",
            "metrics": [],
            "error": None,
        }
        yield {
            "schema_version": "1.0",
            "test_id": "MT-002",
            "suite_type": "multi_turn",
            "status": "FAIL",
            "metrics": [],
            "error": None,
        }

    monkeypatch.setattr(metric_probe, "iter_metric_probe_results", fake_results)

    exit_code = cli.main(["metric", "conversation_memory"])

    assert exit_code == 1
    objects = _decode_json_objects(capsys.readouterr().out)
    assert [item["test_id"] for item in objects] == ["MT-001", "MT-002"]


def test_metric_cli_error_exit_code_has_priority(monkeypatch, capsys):
    def fake_results(metric_key, test_id=None):
        yield {
            "schema_version": "1.0",
            "test_id": "MT-001",
            "suite_type": "multi_turn",
            "status": "FAIL",
            "metrics": [],
            "error": None,
        }
        yield {
            "schema_version": "1.0",
            "test_id": "MT-002",
            "suite_type": "multi_turn",
            "status": "ERROR",
            "metrics": [],
            "error": {"type": "RuntimeError", "message": "boom"},
        }

    monkeypatch.setattr(metric_probe, "iter_metric_probe_results", fake_results)

    exit_code = cli.main(["metric", "conversation_memory"])

    assert exit_code == 2
    objects = _decode_json_objects(capsys.readouterr().out)
    assert [item["status"] for item in objects] == ["FAIL", "ERROR"]
