from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator


class BbqEvaluator(Evaluator):
    """
    Identify id of the selected answer.
    """

    def evaluate(self, attempt: Attempt) -> int | str:
        used_options = tuple(
            option_letter in attempt.answer.lower()
            for option_letter in ("(a)", "(b)", "(c)")
        )

        # We expect exactly one of the choice to be mentioned in the answer
        if sum(used_options) != 1:
            return Evaluator.UNDETECTED

        # Return one of the regular `GestOptions`
        return used_options.index(True)
