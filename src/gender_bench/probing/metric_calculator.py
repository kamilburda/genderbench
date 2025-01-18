from typing import TYPE_CHECKING, Any

import numpy as np

from gender_bench.probing.probe_item import ProbeItem

if TYPE_CHECKING:
    from gender_bench.probing.probe import Probe


class MetricCalculator:
    """
    MetricCalculator calculates arbitrary metrics for a probe that has answers
    generated and evaluated.
    """

    def __init__(self, probe: "Probe"):
        self.probe = probe

    def calculate(self, probe_items: list[ProbeItem]) -> dict[str, Any]:
        """
        Method that calculates all the appropriate metrics for the set-up
        `Probe`.
        """
        raise NotImplementedError

    def __call__(self, probe_items: list[ProbeItem]) -> dict[str, Any]:
        return self.calculate(probe_items)

    @staticmethod
    def filter_undetected(func):
        """
        This decorator can be used for `MetricEvaluator.calculate` methods if
        they use `Evaluator.undetected` as a value in their answer `Enum`.

        (1) Filter out all the `probe_items` that have all the attempts resulted
        in `undetected`.
        (2) Calculate `undetected_rate` based on the filtration.

        The `calculate` methods then do not have to explicitly handle such cases
        as they have a guarantee that at least one attempt had valid answer.
        """

        def is_undetected(evaluation):
            return evaluation is None  # TODO: make this dynamic

        def wrapper_func(self, probe_items):

            filtered_probe_items = [
                item
                for item in probe_items
                if any(
                    not is_undetected(attempt.evaluation) for attempt in item.attempts
                )
            ]
            undetected_rate_items = 1 - len(filtered_probe_items) / len(probe_items)
            undetected_rate_attempts = float(
                np.mean(
                    [
                        is_undetected(attempt.evaluation)
                        for item in probe_items
                        for attempt in item.attempts
                    ]
                )
            )
            metrics = func(self, filtered_probe_items)
            metrics["undetected_rate_items"] = undetected_rate_items
            metrics["undetected_rate_attempts"] = undetected_rate_attempts
            return metrics

        return wrapper_func
