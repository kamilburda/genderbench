from abc import ABC, abstractmethod


class Generator(ABC):
    """`Generator` is an abstract class for text generators that implement
    `generate` method.
    """

    @abstractmethod
    def generate(self, texts: list[str]) -> list[str]:
        """Generate responses for all `texts`.

        Args:
            texts (list[str]): List of prompts that will be send to `generator`.

        Returns:
            list[str]: List of answers.
        """
        raise NotImplementedError
