from genderbench.probing.attempt import Attempt
from genderbench.probing.evaluator import ClosedSetEvaluator


class DiversityMedQaEvaluator(ClosedSetEvaluator):
    """
    Was the correct option selected?
    """

    def __init__(self, probe):
        super().__init__(probe=probe, options=[True, False])

    def calculate_evaluation(self, attempt: Attempt) -> int | str:
        used_options = tuple(
            f"({option_letter})" in attempt.answer.lower() for option_letter in "abcde"
        )

        # We expect exactly one of the choice to be mentioned in the answer
        if sum(used_options) != 1:
            return self.undetected

        selected_option = used_options.index(True)

        return selected_option == attempt.prompt.metadata["correct_option"]
