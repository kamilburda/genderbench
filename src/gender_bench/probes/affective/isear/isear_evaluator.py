from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.probe import Probe


class IsearEvaluator(Evaluator):
    """
    Either return one of the emotions the probe supports or leave it as UNDETECTED.
    """

    def __init__(self, probe: Probe):
        self.probe = probe

    def evaluate(self, attempt: Attempt) -> str:

        answer = attempt.answer.lower().strip().strip(".")

        if answer in self.probe.emotions:
            return answer

        return Evaluator.UNDETECTED
