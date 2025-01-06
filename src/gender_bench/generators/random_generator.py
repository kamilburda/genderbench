import random

from gender_bench.generators.generator import Generator


class RandomGenerator(Generator):

    def __init__(self, options, seed=None):
        self.options = options
        self.set_generator(seed)

    def generate(self, texts):
        return [
            self.random_generator.choice(self.options)
            for _ in range(len(texts))
        ]

    def set_generator(self, seed=None):
        self.random_generator = random.Random(seed)
