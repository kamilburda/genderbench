from openai import OpenAI

client = OpenAI()  # Cannot be pickled


class OpenAiGenerator:

    def __init__(
        self,
        model: str = "gpt-4o",
        max_tokens: int = 100,
        temperature: float = 1.0,
        top_p: int = 1,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def generate(self, input: str):
        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": input}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )

        return completion.choices[0].message.content
