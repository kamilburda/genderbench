from anthropic import AsyncAnthropic

from genderbench.generators.async_api import AsyncApiGenerator


class AnthropicAsyncApiGenerator(AsyncApiGenerator):
    """`AnthropicAsyncApiGenerator` is the `AsyncApiGenerator` subclass that is
    able to call the Anthropic API."""

    def initialize_client(self, base_url, api_key):
        return AsyncAnthropic(api_key=api_key)

    async def call_generation_api(self, text: str) -> str:

        completion = await self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": text}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        answer = completion.content[0].text
        return answer
