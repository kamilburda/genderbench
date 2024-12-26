import json
import os
import random
import uuid
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import List, Literal, Optional

import numpy as np
from scipy.stats import norm
from tqdm import tqdm

from gender_bench.config import LOG_DIR
from gender_bench.generators.generator import Generator
from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.metric_calculator import MetricCalculator

status = Enum(
    "status", ["NEW", "POPULATED", "GENERATED", "EVALUATED", "SCORED", "FINISHED"]
)


class Probe:
    """
    Probe is a test run with a particular generator. It handles the entire
    lifecycle of generating texts, evaluating them, and calcuating final scores.
    """

    def __init__(
        self,
        evaluators: List[Evaluator],
        metric_calculators: List[MetricCalculator],
        num_repetitions: int = 1,
        sample_k: Optional[int] = None,
        calculate_cis: bool = False,
        random_seed: int = 123,
        logging_strategy: Literal["no", "during", "after"] = "no",
    ):
        self.evaluators = evaluators
        self.metric_calculators = metric_calculators
        self.num_repetitions = num_repetitions
        self.sample_k = sample_k
        self.random_seed = random_seed

        self.calculate_cis = calculate_cis
        self.bootstrap_cycles: int = 1000
        self.bootstrap_alpha: float = 0.95

        self.metrics = dict()
        self.status = status.NEW
        self.uuid = uuid.uuid4()
        self.logging_strategy = logging_strategy

    def create_probe_items(self):
        assert self.status == status.NEW
        self.probe_items = self._create_probe_items()
        if self.sample_k is not None:
            self.probe_items = self.sample(k=self.sample_k)
        self.status = status.POPULATED

    def _create_probe_items(self):
        raise NotImplementedError

    def generate(self, generator: Generator):
        assert self.status == status.POPULATED
        for probe_item in tqdm(self.probe_items, desc="Generating"):
            probe_item.generate(generator)
            if self.logging_strategy == "during":
                self.log_json(probe_item.generation_json())
        self.status = status.GENERATED

    def evaluate(self):
        assert self.status == status.GENERATED
        for evaluator in self.evaluators:
            for probe_item in self.probe_items:
                probe_item.evaluate(evaluator)
                if self.logging_strategy == "during":
                    self.log_json(probe_item.evaluation_json(evaluator.__class__))
        self.status = status.EVALUATED

    def calculate_metrics(self):
        assert self.status == status.EVALUATED

        # Bootstrapping
        if self.calculate_cis:
            random.seed(self.random_seed)
            metric_buffer = defaultdict(lambda: list())
            for _ in tqdm(
                range(self.bootstrap_cycles), desc="Bootstrapping"
            ):  # 1000 could be a hyperparameter
                sample_items = random.choices(self.probe_items, k=len(self.probe_items))
                sample_metrics = self.metrics_for_set(sample_items).items()
                for metric, value in sample_metrics:
                    if not np.isnan(value):
                        metric_buffer[metric].append(value)

            metrics = dict()
            for metric_name, values in metric_buffer.items():
                interval = norm.interval(self.bootstrap_alpha, *norm.fit(values))
                metrics[metric_name] = tuple(map(float, interval))  # Retype to float

        # No bootstrapping
        else:
            metrics = self.metrics_for_set(self.probe_items)

        self.status = status.FINISHED
        return metrics

    def metrics_for_set(self, probe_items):
        metrics = dict()
        for metric_calculator in self.metric_calculators:
            metrics.update(metric_calculator.calculate(probe_items))
        return metrics

    def run(self, generator):
        self.create_probe_items()
        if self.logging_strategy == "during":
            self.log_json(self.to_json_dict())
        self.generate(generator)
        self.evaluate()
        self.metrics = self.calculate_metrics()
        if self.logging_strategy == "after":
            self.log_json(self.to_json_dict())
        if self.logging_strategy == "during":
            self.log_json({"Metrics": self.metrics})
        return self.metrics

    def sample(self, k):
        random.seed(self.random_seed)
        return random.sample(self.probe_items, k=k)

    def to_json_dict(self):
        parameters = [
            "uuid",
            "status",
            "metrics",
            "calculate_cis",
            "bootstrap_cycles",
            "bootstrap_alpha",
            "random_seed",
            "sample_k",
            "num_repetitions",
        ]
        d = {parameter: getattr(self, parameter) for parameter in parameters}
        d["probe_items"] = [
            probe_item.to_json_dict() for probe_item in self.probe_items
        ]
        return {"Probe State": d}

    def log_json(self, json_dict):
        log_file = Path(LOG_DIR) / f"{self.uuid}.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(json_dict, default=str) + "\n")
