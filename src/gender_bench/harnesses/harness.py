from typing import Dict, Tuple

from gender_bench.generators.generator import Generator
from gender_bench.probing.probe import Probe

METRICS = Tuple[str]


class Harness:

    def __init__(self, recipe: Dict[Probe, METRICS], calculate_cis: bool = False, logging_strategy: str = None):
        self.recipe = recipe
        self.calculate_cis = calculate_cis
        self.metrics: Dict[Probe, Dict] = dict()

        if logging_strategy is not None:
            for probe in self.probes:
                probe.logging_strategy = logging_strategy

        if calculate_cis is not None:
            for probe in self.probes:
                probe.calculate_cis = self.calculate_cis


    def run(self, generator: Generator):
        for probe in self.recipe:
            probe.run(generator)
            self.metrics[probe] = probe.metrics

        return {
            probe.__class__.__name__: {
                metric: self.metrics[probe][metric] for metric in metrics_of_interest
            }  #
            for probe, metrics_of_interest in self.recipe.items()
        }
    
    @property
    def probes(self):
        return list(self.recipe.keys())
