import warnings

from openai import AsyncAzureOpenAI
from openai import BadRequestError

from genderbench.generators.async_api import AsyncApiGenerator


class AzureOpenAiAsyncApiGenerator(AsyncApiGenerator):
    """`AzureOpenAiAsyncApiGenerator` is the `AsyncApiGenerator` subclass that
    is able to invoke the Azure OpenAI API.

    Args:
        ignore_content_filter_errors (bool): If ``True``, error responses
            related to content filtering by the LLM are ignored. Defaults
            to ``False``.
    """

    def __init__(
            self,
            model: str,
            api_key: str,
            ignore_content_filter_errors: bool = False,
            **kwargs,
    ):
        self._ignore_content_filter_errors = ignore_content_filter_errors

        super().__init__(model, api_key, **kwargs)

    def initialize_client(self, base_url, api_key, **kwargs):
        return AsyncAzureOpenAI(
            azure_endpoint=base_url,
            api_key=api_key,
            **kwargs,
        )

    async def call_generation_api(self, text: str) -> str:
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": text}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            )
        except Exception as e:
            if self._ignore_content_filter_errors and isinstance(e, BadRequestError) and e.code == 'content_filter':
                warnings.warn(f"The following prompt was filtered due to content management policy:\n{text}")
                return ""
            else:
                raise
        else:
            answer = completion.choices[0].message.content
            if answer is None:  # Google AI Studio sometimes returns None
                answer = ""
            return answer
