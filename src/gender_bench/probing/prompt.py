from typing import Dict, Optional
import uuid


class Prompt:
    """
    Prompt is a single text input.

    Attributes
        text : str
            The input text that is used as an input.
        metadata: Dict
            Additional data related to this particular prompt. This is usually
            used to store data related to the expected results, e.g., a correct
            answer for a multiple-choice question.
    """

    def __init__(self, text: str, metadata: Optional[Dict] = None) -> None:
        self.text = text
        self.metadata = metadata
        self.uuid = uuid.uuid4()

    def to_json_dict(self):
        parameters = ["uuid", "text", "metadata"]
        d = {
            parameter: getattr(self, parameter)
            for parameter in parameters
        }
        return d
