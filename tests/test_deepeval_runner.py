from __future__ import annotations

import pytest

from deepeval_runner import metric_success


class MetricWithoutResult:
    name = "incomplete_metric"


def test_metric_without_pass_fail_state_is_an_error():
    with pytest.raises(ValueError, match="did not expose a pass/fail state"):
        metric_success(MetricWithoutResult())