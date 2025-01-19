import uuid
from typing import Any, Optional

from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.prompt import Prompt


class Attempt:
    """
    `Attempt` represents the entire lifecycle of a single call to a `generator`:

        1. The object is initialized with a `Prompt` object representing the input.
        2. `Generator` is used to generate a text `answer` in `Probe.generate`.
        3. Probe's `evaluator` is used to evaluate this `answer` and create an `evaluation`.

    Args:
        prompt (Prompt): Input to a generator.
        repetition_id (int): Repetition index used when a single `Prompt` has
            multiple `Attempts`. See ``Probe.num_repetitions``.

    Attributes:
        answer (str): Text answer generated based on `prompt`.
        evaluation (Any): Evaluation of the `answer`.
        uuid (uuid.UUID): UUID identifier.
    """

    def __init__(self, prompt: Prompt, repetition_id: int) -> None:
        self.answer: Optional[str] = None
        self.evaluation: Any = None
        self.prompt = prompt
        self.repetition_id = repetition_id
        self.uuid: uuid.UUID = uuid.uuid4()

    def evaluate(self, evaluator: Evaluator) -> Any:
        """Send the `Attempt` object to `evaluator` and store the result in
        `evaluation`.

        Args:
            evaluator (Evaluator).

        Returns:
            Any: `evaluator`'s output.
        """
        result = evaluator(self)
        self.evaluation = result
        return result

    def to_json_dict(self) -> dict:
        """Prepare a JSON-serializable dictionary representation. Used for
        logging.

        Returns:
            dict: JSON-serializable dictionary.
        """
        parameters = ["uuid", "repetition_id", "answer", "evaluation"]
        d = {parameter: getattr(self, parameter) for parameter in parameters}
        d["prompt"] = self.prompt.to_json_dict()
        return d
