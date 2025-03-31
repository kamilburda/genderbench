import json
import os
import uuid
from pathlib import Path

from genderbench.config import get_env_variable
from genderbench.generators.generator import Generator
from genderbench.probing.probe import Probe


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
        results (dict[str, dict]): Stores all the results from the probes. Keys
            are probe class names, values are dictionaries with necessary
            information about the results of each probe.
        uuid (uuid.UUID): UUID identifier.
    """

    def __init__(
        self,
        probes: list[Probe],
        log_dir: str = None,
        **kwargs,
    ):
        self.probes = probes
        self.results: dict[str, dict] = dict()
        self.uuid = uuid.uuid4()

        if log_dir is None:
            log_dir = get_env_variable("GENDER_BENCH_LOG_DIR")
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
            probe_results = {
                "class": probe.__class__.__name__,
                "marks": probe.marks,
                "metrics": probe.metrics,
                "probe_uuid": probe.uuid,
            }
            self.results[probe.__class__.__name__] = probe_results
            self.log_results(probe_results)

        return self.marks, self.metrics

    def log_results(self, probe_results):
        """Log calculated `marks` and `metrics` into a file."""
        log_file = self.log_dir / f"{self.__class__.__name__.lower()}_{self.uuid}.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(probe_results, default=str) + "\n")

    @property
    def marks(self):
        """Dictionary of all the marks for individual probes.

        Returns:
            dict[str, dict]
        """
        return {
            probe_name: result["marks"] for probe_name, result in self.results.items()
        }

    @property
    def metrics(self):
        """Dictionary of all the metrics for individual probes.

        Returns:
            dict[str, dict]
        """
        return {
            probe_name: result["metrics"] for probe_name, result in self.results.items()
        }
