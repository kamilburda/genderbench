import asyncio

import nest_asyncio
from openai import AsyncOpenAI


class OpenAiGenerator:

    def __init__(
        self,
        base_url=None,
        api_key=None,
        max_concurrent_tasks=1,
        model: str = "gpt-4o",
        max_tokens: int = 100,
        temperature: float = 1.0,
        top_p: int = 1,
    ):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

        self.max_concurrent_tasks = max_concurrent_tasks

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def generate(self, inputs: list[str]) -> list[str]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Python script
            return asyncio.run(self._generate(inputs))
        else:
            # Jupyter
            nest_asyncio.apply()
            return loop.run_until_complete(self._generate(inputs))

    async def _generate(self, inputs: list[str]) -> list[str]:
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        tasks = [self.generate_single(input, semaphore) for input in inputs]
        results = await asyncio.gather(*tasks)
        return results

    async def generate_single(self, input: str, semaphore: asyncio.Semaphore) -> str:
        async with semaphore:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": input}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            return completion.choices[0].message.content
