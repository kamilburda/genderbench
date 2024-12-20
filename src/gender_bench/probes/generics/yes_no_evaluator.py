from enum import Enum

import nltk
from nltk.tokenize import word_tokenize

from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator


class YesNoEvaluator(Evaluator):
    """
    Detect Yes or No.
    """

    class Answer(Enum):
        YES = "yes"
        NO = "no"
        UNDETECTED = Evaluator.UNDETECTED  # We were not able to detect the answer

    def __init__(self):
        super().__init__()
        nltk.download("punkt", quiet=True)

    def evaluate(self, attempt: Attempt) -> Answer:
        tokens = word_tokenize(attempt.answer.lower())
        contains_yes, contains_no = "yes" in tokens, "no" in tokens
        if contains_yes == contains_no:
            return self.Answer.UNDETECTED
        if contains_yes:
            return self.Answer.YES
        return self.Answer.NO
