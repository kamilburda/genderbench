from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import numpy as np

from genderbench.probing.probe_item import ProbeItem

if TYPE_CHECKING:
    from genderbench.probing.probe import Probe


class MetricCalculator(ABC):
    """`MetricCalculator` is able to calculate all the predetermined metrics for
    its corresponding probe.

    Args:
        probe (Probe): The `probe` that initialized this `MetricCalculator`.
    """

    def __init__(self, probe: "Probe"):
        self.probe = probe

    @property
    def undetected(self) -> Any:
        """The `undetected` value used by the `evaluator` from the corresponding
        probe.

        Returns:
            Any: The value that is being used.
        """
        return self.probe.evaluator.undetected

    @abstractmethod
    def calculate(self, probe_items: list[ProbeItem]) -> dict[str, float]:
        """Perform the core metric calculation routine for `probe_items`.

        Args:
            probe_items (list[ProbeItem]): `ProbeItems` that already have
                answers generated and evaluated.

        Returns:
            dict[str, Any]: Calculated metrics.
        """
        raise NotImplementedError

    def __call__(self, probe_items: list[ProbeItem]) -> dict[str, float]:
        return self.calculate(probe_items)

    @staticmethod
    def filter_undetected(func: callable) -> callable:
        """Decorator used to handle `undetected` values in for
        `MetricCalculator.calculate` methods. This decorator has two functions:

            1. It filters out those input `probe_items` that have ALL their
            `Attempts` set as `evaluation_undetected`.

            2. It calculate two metrics `undetected_rate_attempts` and
            `undetected_rate_items` that say how many `Attempts` and
            `ProbeItems` respectively had undetected evaluation.

        Args:
            func (callable[list[ProbeItem], dict[str, Any]]): The `calculate`
                method to be decorated.

        Returns:
            callable: Decorated `calculate` method.
        """

        def wrapper_func(self, probe_items: list[ProbeItem]) -> dict[str, float]:

            filtered_probe_items = [
                item
                for item in probe_items
                if not all(attempt.evaluation_undetected for attempt in item.attempts)
            ]
            undetected_rate_items = 1 - len(filtered_probe_items) / len(probe_items)
            undetected_rate_attempts = float(
                np.mean(
                    [
                        attempt.evaluation_undetected
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
