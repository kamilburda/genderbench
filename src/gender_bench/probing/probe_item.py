import uuid
from typing import Any, Optional

from gender_bench.generators.generator import Generator
from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.prompt import Prompt


class ProbeItem:
    """
    `ProbeItem` is a single test item in the probing process. It can consist of
    multiple prompts. For example, a single multiple-choice question is a
    `ProbeItem`. To address *ordering bias*, we can have multiple prompts with
    different answer orders within a single `ProbeItem`.

    This class also handles repetitions that can be requested for each `prompt`.
    """

    def __init__(
        self,
        prompts: list[Prompt],
        num_repetitions: int,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.prompts = prompts
        self.num_repetitions = num_repetitions
        self.metadata = metadata
        self.uuid = uuid.uuid4()

        self.attempts: list[Attempt] = [
            Attempt(prompt, repetition_id)
            for prompt in self.prompts
            for repetition_id in range(self.num_repetitions)
        ]

    def generate(self, generator: Generator) -> None:
        for attempt in self.attempts:
            attempt.generate(generator)
            # self.log(generation)

    def evaluate(self, evaluator: Evaluator) -> None:
        for attempt in self.attempts:
            attempt.evaluate(evaluator)
            # self.log(evaluation)

    def to_json_dict(self):
        parameters = ["uuid", "num_repetitions", "metadata"]
        d = {parameter: getattr(self, parameter) for parameter in parameters}
        d["prompts"] = [prompt.to_json_dict() for prompt in self.prompts]
        d["attempts"] = [attempt.to_json_dict() for attempt in self.attempts]
        return d
