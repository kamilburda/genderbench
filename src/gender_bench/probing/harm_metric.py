import numpy as np


class HarmMetric:
    """
    HarmMetric represents a metric that measure a specific gender-related harm.
    The class contains data about how to interpret the values from the metric.

    HarmMetric contains mark ranges -- intervals that say what is the overall
    mark for any given value of the metric. The marks go from 0 (the best mark)
    up (3 is the worst).

    The interprations is:
    - 0: Healthy
    - 1: Cautionary
    - 2: Critical
    - 3: Catastrophic
    """

    def __init__(self, mark_ranges: dict, harm_types: list[str], description: str):
        # mark_ranges = {0: [(0, 1)], 1: [(1, 2)]}
        if isinstance(mark_ranges, dict):
            self.mark_ranges = mark_ranges
        # mark_ranges = [0, 1, 2]
        elif isinstance(mark_ranges, list):
            self.mark_ranges = {
                i: [(mn, mx)]
                for i, (mn, mx) in enumerate(zip(mark_ranges, mark_ranges[1:]))
            }

        assert sorted(self.mark_ranges.keys()) == list(range(4))

        self.harm_types = harm_types
        self.description = description

    def calculate_mark(self, value):
        if isinstance(value, float) and np.isnan(value):
            return np.nan
        if isinstance(value, tuple) and np.isnan(value[0]) and np.isnan(value[1]):
            return np.nan
        return min(
            mark
            for mark, ranges in self.mark_ranges.items()
            for range in ranges
            if self.range_overlap(value, range)
        )

    @staticmethod
    def range_overlap(value, range):
        min_range, max_range = range

        # No confidence interval
        if isinstance(value, float):
            return min_range <= value <= max_range

        # Confidence interval
        min_ci, max_ci = value
        return max_ci >= min_range and min_ci <= max_range

    @property
    def metric_range(self):
        mins, maxs = zip(
            *(range for ranges in self.mark_ranges.values() for range in ranges)
        )
        return min(mins), max(maxs)
