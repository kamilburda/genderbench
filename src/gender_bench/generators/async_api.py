import asyncio
from abc import ABC, abstractmethod

import nest_asyncio
from tqdm.asyncio import tqdm


class AsyncApiGenerator(ABC):
    """`AsyncApiGenerator` is an abstract class that provides ``asyncio`` calls
    to different APIs. The code supports various generation parameters,
    arbitrary number of concurrent tasks, and retrying mechanism.

    Args:
        model (str): Name of the requested model.
        api_key (str): API key.
        base_url (str, optional): Base URL for the API. Defaults to None.
        max_concurrent_tasks (int, optional): Maximum number of tasks running in
            parallel. Set this in accordance with the usage policy of your API
            provider. Defaults to 1.
        max_tokens (int, optional): Maximum number of tokens to generate.
            Defaults to 300.
        temperature (float, optional): Defaults to 1.0.
        top_p (float, optional): Defaults to 1.0.
        retry_count (int, optional): How many time is the API called before an
            exception is raised. Defaults to 10.
        retry_delay (float, optional): How long (in seconds) is the delay
            between retries initially. Defaults to 1.0.
        retry_backoff (float, optional): How much does the delay increases after
            each failed retry. Defaults to 2.0.

    Attributes:
        client: A client object that is used to make requests.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = None,
        max_concurrent_tasks: int = 1,
        max_tokens: int = 300,
        temperature: float = 1.0,
        top_p: float = 1.0,
        retry_count: int = 10,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
    ):
        self.base_url = base_url
        self.client = self.initialize_client(base_url=base_url, api_key=api_key)
        self.max_concurrent_tasks = max_concurrent_tasks
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

        assert retry_count > 0
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff

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
            return loop.run_until_complete(self.async_generate(texts))

    async def async_generate(self, texts: list[str]) -> list[str]:
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        tasks = [self.generate_single(text, semaphore) for text in texts]
        answers = await tqdm.gather(*tasks)
        return answers

    async def generate_single(self, text: str, semaphore: asyncio.Semaphore) -> str:

        async with semaphore:
            attempt = 0
            current_delay = self.retry_delay

            while True:
                try:
                    return await self.call_generation_api(text)
                except Exception:
                    attempt += 1
                    if attempt == self.retry_count:
                        raise
                    await asyncio.sleep(current_delay)
                    current_delay *= self.retry_backoff

    @abstractmethod
    def initialize_client(self, base_url, api_key):
        raise NotImplementedError

    @abstractmethod
    async def call_generation_api(self, text: str) -> str:
        raise NotImplementedError
