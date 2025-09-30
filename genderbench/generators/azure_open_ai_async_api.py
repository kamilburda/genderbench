from openai import AsyncAzureOpenAI

from genderbench.generators.async_api import AsyncApiGenerator


class AzureOpenAiAsyncApiGenerator(AsyncApiGenerator):
    """`AzureOpenAiAsyncApiGenerator` is the `AsyncApiGenerator` subclass that
    is able to invoke the Azure OpenAI API.
    """

    def initialize_client(self, base_url, api_key, **kwargs):
        return AsyncAzureOpenAI(
            azure_endpoint=base_url,
            api_key=api_key,
            **kwargs,
        )

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
