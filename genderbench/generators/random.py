import random

from genderbench.generators.generator import Generator


class RandomGenerator(Generator):
    """`RandomGenerator` is a simple generator that can be used for debugging
    purposes.

    Args:
        options (list[str]): Possible generations that will be samples with
            uniform distribution.
        seed (int, optional): Random seed that controls the sampling process.
    """

    def __init__(self, options: list[str], seed: int = None):
        self.options = options
        self.set_generator(seed)

    def generate(self, texts: list[str]) -> list[str]:
        """Generate responses for all `texts` by sampling `options`.

        Args:
            texts (list[str]): List of prompts that will be send to `generator`.

        Returns:
            list[str]: List of answers.
        """
        return [self.random_generator.choice(self.options) for _ in range(len(texts))]

    def set_generator(self, seed: int = None):
        self.random_generator = random.Random(seed)
