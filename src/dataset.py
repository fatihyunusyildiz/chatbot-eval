from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


def load_json_dataset(path: str | Path) -> list[dict[str, Any]]:
    dataset_path = Path(path)
    if not dataset_path.is_absolute():
        dataset_path = ROOT_DIR / dataset_path

    with dataset_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Dataset must be a JSON array: {dataset_path}")
    return data


def load_single_turn_dataset() -> list[dict[str, Any]]:
    return load_json_dataset(DATA_DIR / "golden_single_turn.json")


def load_multi_turn_dataset() -> list[dict[str, Any]]:
    return load_json_dataset(DATA_DIR / "golden_multi_turn.json")
