import json
import os
import uuid
from pathlib import Path

from gender_bench.config import LOG_DIR
from gender_bench.generators.generator import Generator
from gender_bench.probing.probe import Probe


class Harness:
    """`Harness` represents a predefined set of `Probes` that are supposed to
    be run together to provide a comprehensive evaluation for `generator`.

    Args:
        probes (list[Probe]): Probe in ``status.NEW``.
        log_dir (str, optional): A logging path. If set to None, environment
            variable `LOG_DIR` is used instead.
        **kwargs: Arguments from the following list will be set for all
            `probes`: `log_strategy`, `log_dir`, `calculate_cis`,
            `bootstrap_cycles`, `bootstrap_alpha`. See `Probe` for more details.

    Attributes:
        metrics (dict[str, float]): Calculated metrics. Available only after
            `run` was run.
        marks (dict[str, dict]): Calculated marks. Available only after
            `run` was run.
        uuid (uuid.UUID): UUID identifier.
    """

    def __init__(
        self,
        probes: list[Probe],
        log_dir: str = None,
        **kwargs,
    ):
        self.probes = probes
        self.metrics: dict[Probe, dict] = dict()
        self.marks: dict[Probe, dict] = dict()
        self.uuid = uuid.uuid4()

        if log_dir is None:
            log_dir = LOG_DIR
        self.log_dir = Path(log_dir)

        attributes_to_set = dict(kwargs) | {"log_dir": self.log_dir}
        for arg_name, arg_value in attributes_to_set.items():
            assert arg_name in (
                "log_strategy",
                "log_dir",
                "calculate_cis",
                "bootstrap_cycles",
                "bootstrap_alpha",
            )
            for probe in self.probes:
                setattr(probe, arg_name, arg_value)

    def run(self, generator: Generator) -> tuple[dict[str, dict], dict[str, float]]:
        """Iteratively run all `probes` and store the results into a JSONL file.

        Args:
            generator (Generator): Evaluated text generator.

        Returns:
            tuple[dict[str, dict]], dict[str, float]: A tuple containing:

                - Dictionary describing the calculated marks.
                - Dictionary with metrics and their values.
        """
        for probe in self.probes:
            probe.run(generator)
            self.metrics[probe.__class__.__name__] = probe.metrics
            self.marks[probe.__class__.__name__] = probe.marks
            self.log_results()

        return self.marks, self.metrics

    def log_results(self):
        """Log calculated `marks` and `metrics` into a file."""
        log_file = self.log_dir / f"{self.uuid}.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        data = {
            "metrics": self.metrics,
            "marks": self.marks,
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(data, default=str) + "\n")
