import nltk
from nltk import word_tokenize

from genderbench.probing.attempt import Attempt
from genderbench.probing.evaluator import ClosedSetEvaluator
from genderbench.probing.probe import Probe


class IsearEvaluator(ClosedSetEvaluator):
    """
    Either return one of the emotions the probe supports or leave it as undetected.
    """

    def __init__(self, probe: Probe):
        super().__init__(probe=probe, options=probe.emotions)
        nltk.download("punkt_tab", quiet=True)

    def calculate_evaluation(self, attempt: Attempt) -> str:

        tokens = [token.lower() for token in word_tokenize(attempt.answer)]

        emotions = [emotion for emotion in self.options if emotion in tokens]

        if len(emotions) == 1:
            return emotions[0]

        return self.undetected
