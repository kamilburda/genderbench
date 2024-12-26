import json
import os
from pathlib import Path
from typing import Dict, Tuple
import uuid

from gender_bench.config import LOG_DIR
from gender_bench.generators.generator import Generator
from gender_bench.probing.probe import Probe

METRICS = Tuple[str]


class Harness:

    def __init__(
        self,
        probes: list[Probe],
        calculate_cis: bool = False,
        logging_strategy: str = None,
    ):
        self.probes = probes
        self.calculate_cis = calculate_cis
        self.metrics: Dict[Probe, Dict] = dict()
        self.uuid = uuid.uuid4()

        if logging_strategy is not None:
            for probe in self.probes:
                probe.logging_strategy = logging_strategy

        if calculate_cis is not None:
            for probe in self.probes:
                probe.calculate_cis = self.calculate_cis

    def run(self, generator: Generator):
        for probe in self.probes:
            probe.run(generator)
            self.metrics[probe.__class__.__name__] = probe.metrics

        return self.metrics
    
    def log_metrics(self):
        log_file = Path(LOG_DIR) / f"{self.uuid}.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(self.metrics, default=str) + "\n")
