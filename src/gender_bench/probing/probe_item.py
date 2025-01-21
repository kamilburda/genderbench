import uuid
from typing import Any, Optional

from gender_bench.probing.attempt import Attempt
from gender_bench.probing.prompt import Prompt


class ProbeItem:
    """`ProbeItem` is a single test item for `Probe`. Its main role is to group
    related `Attempts` into a single evaluated entity when metrics are
    calculated. The sampling process performed during confidence interval
    calculations is also done on a `ProbeItem` level. For this reason, it is
    recommended to group related `Prompts` into a single `ProbeItem` to avoid
    overconfident inverval ranges.

    `ProbeItem` object handles the creation of multiple `Attempts` with
    identical `Prompts` when `num_repetitions` is used in `Probe`.

    Note:

        Apart from repetitions, `ProbeItem` can be used to group very similar
        prompts that we do not want to necessarily treat as separate entities.
        For example, multiple orderings of options for a
        multiple-choice question can be grouped within one `ProbeItem`.

    Args:
        prompts (list[Prompt]): `Prompts` that will be used to create new
            `Attempts`.
        num_repetitions (int): How many `Attempts` will be created for each
            `Prompt`.
        metadata (Optional[dict[str, Any]], optional): Metadata related to `ProbeItem`
            that can be used during metric calculation process.

    Attributes:
        uuid (uuid.UUID): UUID identifier.
        attempts (list[Attempt]): The list of `Attempts` belonging to
            `ProbeItem`.

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
        self.uuid: uuid.UUID = uuid.uuid4()

        self.attempts: list[Attempt] = [
            Attempt(prompt, repetition_id)
            for prompt in self.prompts
            for repetition_id in range(self.num_repetitions)
        ]

    def to_json_dict(self) -> dict:
        """Prepare a JSON-serializable dictionary representation. Used for
        logging.

        Returns:
            dict: JSON-serializable dictionary.
        """
        parameters = ["uuid", "num_repetitions", "metadata"]
        d = {parameter: getattr(self, parameter) for parameter in parameters}
        d["prompts"] = [prompt.to_json_dict() for prompt in self.prompts]
        d["attempts"] = [attempt.to_json_dict() for attempt in self.attempts]
        return d
