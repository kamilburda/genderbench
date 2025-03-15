from openai import AsyncOpenAI

from genderbench.generators.async_api import AsyncApiGenerator


class OpenAiAsyncApiGenerator(AsyncApiGenerator):
    """`OpenAiAsyncApiGenerator` is the `AsyncApiGenerator` subclass that is
    able to call OpenAI-style APIs. These are generally supported by a variety
    of API providers other than OpenAI. ``base_url`` can be used to query these
    providers."""

    def initialize_client(self, base_url, api_key):
        return AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def call_generation_api(self, text: str) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": text}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        answer = completion.choices[0].message.content
        if answer is None:  # Google AI Studio sometimes returns None
            answer = ""
        return answer
