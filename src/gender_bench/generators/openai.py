import asyncio

import nest_asyncio
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm


class OpenAiGenerator:

    def __init__(
        self,
        base_url=None,
        api_key=None,
        max_concurrent_tasks=1,
        model: str = "gpt-4o",
        max_tokens: int = 300,
        temperature: float = 1.0,
        top_p: int = 1,
    ):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

        self.max_concurrent_tasks = max_concurrent_tasks

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def generate(self, texts: list[str]) -> list[str]:
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
