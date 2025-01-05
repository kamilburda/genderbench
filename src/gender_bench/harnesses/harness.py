import json
import os
import uuid
from pathlib import Path
from typing import Tuple

from gender_bench.config import LOG_DIR
from gender_bench.generators.generator import Generator
from gender_bench.probing.probe import Probe

METRICS = Tuple[str]


class Harness:

    def __init__(
        self,
        probes: list[Probe],
        **kwargs,
    ):
        self.probes = probes
        self.metrics: dict[Probe, dict] = dict()
        self.marks: dict[Probe, dict] = dict()
        self.uuid = uuid.uuid4()

        for arg_name, arg_value in kwargs.items():
            assert arg_name in (
                "logging_strategy",
                "calculate_cis",
                "bootstrap_cycles",
                "bootstrap_alpha",
            )
            for probe in self.probes:
                setattr(probe, arg_name, arg_value)

    def run(self, generator: Generator):
        for probe in self.probes:
            probe.run(generator)
            self.metrics[probe.__class__.__name__] = probe.metrics
            self.marks[probe.__class__.__name__] = probe.marks
            self.log_metrics()

        return self.marks, self.metrics

    def log_metrics(self):
        log_file = Path(LOG_DIR) / f"{self.uuid}.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        data = {
            "Metrics": self.metrics,
            "Marks": self.marks,
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(data, default=str) + "\n")
