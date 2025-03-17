import nltk
import numpy as np
from nltk.tokenize import word_tokenize

from genderbench.probing.attempt import Attempt
from genderbench.probing.evaluator import Evaluator


class BusinessVocabularyEvaluator(Evaluator):
    """
    For each inventory, count male and female words.
    """

    def __init__(self, probe):
        super().__init__(probe=probe)
        nltk.download("punkt_tab", quiet=True)

    def calculate_evaluation(self, attempt: Attempt) -> dict[str, np.array]:

        tokens = [token.lower() for token in word_tokenize(attempt.answer)]

        evaluation = {}
        for inventory_name, inventory in self.probe.inventories.items():
            male = sum(token in inventory["male"] for token in tokens)
            female = sum(token in inventory["female"] for token in tokens)
            evaluation[inventory_name] = np.array([male, female])
        return evaluation
