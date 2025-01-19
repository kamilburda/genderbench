import asyncio

import nest_asyncio
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm


class OpenAiGenerator:
    """`OpenAiGenerator` implements ``asyncio`` calls to OpenAI-style APIs.
    The code supports various generation parameters, arbitrary number of
    concurrent tasks, and retrying mechanism.

    Args:
        model (str): Name of the requested model.
        base_url (str): Base URL for the API.
        api_key (str): API key.
        max_concurrent_tasks (int, optional): Maximum number of tasks running in
            parallel. Set this in accordance with the usage policy of your API
            provider. Defaults to 1.
        max_tokens (int, optional): Maximum number of tokens to generate.
            Defaults to 300.
        temperature (float, optional): Defaults to 1.0.
        top_p (float, optional): Defaults to 1.0.

    Attributes:
        client (AsyncOpenAI): A client object that is used to make requests.
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str,
        max_concurrent_tasks: int = 1,
        max_tokens: int = 300,
        temperature: float = 1.0,
        top_p: float = 1.0,
    ):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

        self.max_concurrent_tasks = max_concurrent_tasks

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def generate(self, texts: list[str]) -> list[str]:
        """Generate responses for all `texts` by calling `client`.

        Args:
            texts (list[str]): List of prompts that will be send to `generator`.

        Returns:
            list[str]: List of answers.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Python script
            return asyncio.run(self._generate(texts))
        else:
            # Jupyter
            nest_asyncio.apply()
            return loop.run_until_complete(self._generate(texts))

    async def _generate(self, texts: list[str]) -> list[str]:
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        tasks = [self.generate_single(text, semaphore) for text in texts]
        answers = await tqdm.gather(*tasks)
        return answers

    async def generate_single(self, text: str, semaphore: asyncio.Semaphore) -> str:
        delay = 1
        tries = 10
        backoff = 2

        async with semaphore:
            attempt = 0
            current_delay = delay

            while attempt < tries:
                try:
                    return await self.call_generation_api(text)
                except Exception:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

    async def call_generation_api(self, text: str) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": text}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        answer = completion.choices[0].message.content
        return answer
