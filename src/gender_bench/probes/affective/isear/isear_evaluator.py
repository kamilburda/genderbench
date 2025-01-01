import nltk
from nltk import word_tokenize

from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.probe import Probe


class IsearEvaluator(Evaluator):
    """
    Either return one of the emotions the probe supports or leave it as UNDETECTED.
    """

    def __init__(self, probe: Probe):
        super().__init__()
        self.probe = probe
        nltk.download("punkt", quiet=True)

    def evaluate(self, attempt: Attempt) -> str:

        tokens = [token.lower() for token in word_tokenize(attempt.answer)]

        emotions = [emotion for emotion in self.probe.emotions if emotion in tokens]

        if len(emotions) == 1:
            return emotions[0]

        return Evaluator.UNDETECTED
