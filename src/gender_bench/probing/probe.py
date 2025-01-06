import json
import os
import random
import uuid
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

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
        evaluator: Evaluator,
        metric_calculator: MetricCalculator,
        num_repetitions: int = 1,
        sample_k: Optional[int] = None,
        calculate_cis: bool = False,
        bootstrap_cycles: int = 1000,
        bootstrap_alpha: float = 0.95,
        random_seed: int = 123,
        logging_strategy: Literal["no", "during", "after"] = "no",
    ):
        self.evaluator = evaluator
        self.metric_calculator = metric_calculator

        self.num_repetitions = num_repetitions
        self.sample_k = sample_k
        self.random_seed = random_seed

        self.calculate_cis = calculate_cis
        self.bootstrap_cycles = bootstrap_cycles
        self.bootstrap_alpha = bootstrap_alpha

        self.metrics = dict()
        self.marks = dict()
        self.status = status.NEW
        self.uuid = uuid.uuid4()
        self.logging_strategy = logging_strategy

        self.probe_items = list()

    def __repr__(self):
        num_items = len(self.probe_items)
        num_attempts = sum(len(item.attempts) for item in self.probe_items)
        return f"<{self.__class__.__name__}: {num_items=}, {num_attempts=}>"

    def create_probe_items(self):
        assert self.status == status.NEW
        self.create_probe_items_random_generator = random.Random(self.random_seed)
        self.probe_items = self._create_probe_items()
        if self.sample_k is not None:
            self.probe_items = self.sample(k=self.sample_k)
        self.status = status.POPULATED
        if self.logging_strategy == "during":
            self.log_json(self.to_json_dict())

    def _create_probe_items(self):
        raise NotImplementedError

    def generate(self, generator: Generator):
        assert self.status == status.POPULATED
        texts = [
            attempt.prompt.text
            for item in self.probe_items
            for attempt in item.attempts
        ]

        answers = generator.generate(texts)
        answers_iterator = iter(answers)

        for item in self.probe_items:
            for attempt in item.attempts:
                attempt.answer = next(answers_iterator)

        if self.logging_strategy == "during":
            self.log_json(self.to_json_dict())
        self.status = status.GENERATED

    def evaluate(self):
        assert self.status == status.GENERATED
        for probe_item in self.probe_items:
            probe_item.evaluate(self.evaluator)
        if self.logging_strategy == "during":
            self.log_json(self.to_json_dict())
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
                    metric_buffer[metric].append(value)

            metrics = dict()
            for metric_name, values in metric_buffer.items():
                if all(np.isnan(value) for value in values):
                    interval = (np.nan, np.nan)
                else:
                    values = [value for value in values if not np.isnan(value)]
                    interval = norm.interval(self.bootstrap_alpha, *norm.fit(values))
                    interval = tuple(map(float, interval))
                metrics[metric_name] = interval

        # No bootstrapping
        else:
            metrics = self.metrics_for_set(self.probe_items)

        self.metrics = metrics
        if self.harm_metrics:
            self.marks = self.calculate_marks()
        self.status = status.FINISHED

        if self.logging_strategy in ("during", "after"):
            self.log_json(self.to_json_dict())

    def metrics_for_set(self, probe_items):
        return self.metric_calculator.calculate(probe_items)

    def calculate_marks(self):
        return {
            metric_name: {
                "mark": harm_metric.calculate_mark(self.metrics[metric_name]),
                "value": self.metrics[metric_name],
                "description": harm_metric.description,
                "harm_types": harm_metric.harm_types,
                "mark_ranges": harm_metric.mark_ranges,
            }
            for metric_name, harm_metric in self.harm_metrics.items()
        }

    def run(self, generator):
        self.create_probe_items()
        self.generate(generator)
        self.evaluate()
        self.calculate_metrics()
        return self.marks, self.metrics

    def sample(self, k):
        random.seed(self.random_seed)
        return random.sample(self.probe_items, k=k)

    def to_json_dict(self):
        parameters = [
            "uuid",
            "status",
            "metrics",
            "marks",
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

    @property
    def attempts(self):
        for item in self.probe_items:
            for attempt in item.attempts:
                yield attempt
