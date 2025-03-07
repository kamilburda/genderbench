from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.probe import Probe


class MachineTranslationEvaluator(Evaluator):
    """
    Determine if the translated sentence uses the male or female gender, or leave it as undetected.
    """

    def __init__(self, probe: Probe):
        super().__init__(probe=probe)

    def calculate_evaluation(self, attempt: Attempt) -> str:
        return self.undetected
