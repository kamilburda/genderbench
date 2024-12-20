from typing import Any, Dict, List, Optional
import uuid

from gender_bench.generators.generator import Generator
from gender_bench.probing.attempt import Attempt
from gender_bench.probing.evaluator import Evaluator
from gender_bench.probing.prompt import Prompt


class ProbeItem:
    """
    `ProbeItem` is a single test item in the probing process. It can consist of
    multiple prompts. For example, a single multiple-choice question is a
    `ProbeItem`. To address _ordering bias_, we can have multiple prompts with
    different answer orders within a single `ProbeItem`.

    This class also handles repetitions that can be requested for each `prompt`.
    """

    def __init__(
        self,
        prompts: List[Prompt],
        num_repetitions: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.prompts = prompts
        self.num_repetitions = num_repetitions
        self.metadata = metadata
        self.uuid = uuid.uuid4()

        self.attempts: List[Attempt] = [
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
        d = {
            parameter: getattr(self, parameter)
            for parameter in parameters
        }
        d["prompts"] = [prompt.to_json_dict() for prompt in self.prompts]
        d["attempts"] = [attempt.to_json_dict() for attempt in self.attempts]
        return d
    
    def generation_json(self):
        return {"Probe Item Generation":[
            {
                "uuid": attempt.uuid,
                "answer": attempt.answer,
            }
            for attempt in self.attempts
        ]}
    
    def evaluation_json(self, evaluator):
        return {"Probe Item Evaluation":[
            {
                "uuid": attempt.uuid,
                "evaluation": {evaluator.__module__ + "." + evaluator.__name__: attempt.evaluation[evaluator]},
            }
            for attempt in self.attempts
        ]}