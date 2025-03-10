import random


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
        # TODO: Return one of the following based on `attempt.answer` and `attempt.prompt.metadata`:
        # * "male" - if the gender detected from the translation is male
        # * "female" - if the gender detected from the translation is female
        # * "undetected" - if the gender could not be determined, the gender is neither male nor female, or the translation is not correct
        possible_results = ["male", "female", "undetected"]

        return possible_results[random.randint(0, len(possible_results) - 1)]
