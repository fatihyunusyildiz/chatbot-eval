from __future__ import annotations

import pytest

from chatbot_eval.golden_case_selector import select_golden_cases


def test_selects_all_metric_cases_in_dataset_order():
    cases = select_golden_cases("correction_handling")

    assert [item["test_id"] for item in cases] == ["MT-005", "MT-014", "MT-015"]


def test_rejects_test_case_that_does_not_belong_to_metric():
    with pytest.raises(ValueError, match="not compatible"):
        select_golden_cases("correction_handling", test_id="MT-001")