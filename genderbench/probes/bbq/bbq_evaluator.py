from genderbench.probing.attempt import Attempt
from genderbench.probing.evaluator import ClosedSetEvaluator


class BbqEvaluator(ClosedSetEvaluator):
    """
    Identify id of the selected answer.
    """

    def __init__(self, probe):
        super().__init__(probe=probe, options=["a", "b", "c"])

    def calculate_evaluation(self, attempt: Attempt) -> int | str:
        used_options = tuple(
            f"({option_letter})" in attempt.answer.lower()
            for option_letter in self.options
        )

        # We expect exactly one of the choice to be mentioned in the answer
        if sum(used_options) != 1:
            return self.undetected

        # Return one of the regular `GestOptions`
        return self.options[used_options.index(True)]
