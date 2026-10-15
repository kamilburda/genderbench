import asyncio
import math
import time
from typing import Any

from openai import AsyncOpenAI

from genderbench.generators.async_api import AsyncApiGenerator
from genderbench.probing.prompt import Prompt


class OpenRouterDecisionsAsyncApiGenerator(AsyncApiGenerator[Prompt]):
    """Call OpenRouter's Decisions API with per-prompt choice criteria.

    Use ``generate_prompts(prompts)`` (or ``await async_generate(prompts)``).
    Each prompt must supply ``decisions``, mapping evaluator-compatible answer
    labels to descriptions. The API's selected choice is returned unchanged.
    Only prompt text and decisions are sent; evaluation metadata stays local.

    ``base_url`` defaults to ``https://openrouter.ai/api/alpha``. Unlike chat
    completions, this endpoint accepts state/questions and has no sampling or
    text-generation parameters. Extra keyword arguments configure AsyncOpenAI
    (for example, ``timeout`` or ``http_client``).

    ``requests_per_minute`` optionally limits request starts per generator,
    including retries and successive probe batches. Requests are evenly spaced
    without bursts; 3000 means one start every 0.02 seconds. Defaults to None
    (unlimited). ``max_concurrent_tasks`` independently limits in-flight work.
    When rate limiting is enabled, use ``retry_count`` for retries and leave
    the SDK's ``max_retries`` at zero so every retry passes through the limiter.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/alpha",
        max_concurrent_tasks: int = 1,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
        requests_per_minute: float | None = None,
        **initialize_client_kwargs,
    ):
        if max_concurrent_tasks < 1:
            raise ValueError("max_concurrent_tasks must be at least 1")
        if requests_per_minute is not None:
            if not math.isfinite(requests_per_minute) or requests_per_minute <= 0:
                raise ValueError("requests_per_minute must be a positive finite number")
            if initialize_client_kwargs.get("max_retries", 0) != 0:
                raise ValueError(
                    "Use retry_count with rate limiting; max_retries must be 0"
                )
        self.requests_per_minute = requests_per_minute
        self._next_request_at = 0.0
        self._rate_limit_loop = None
        self._rate_limit_lock = None
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            max_concurrent_tasks=max_concurrent_tasks,
            retry_count=retry_count,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            **initialize_client_kwargs,
        )

    def initialize_client(self, base_url, api_key, **kwargs):
        # Let AsyncApiGenerator control retries rather than nesting retry loops.
        kwargs.setdefault("max_retries", 0)
        return AsyncOpenAI(base_url=base_url, api_key=api_key, **kwargs)

    def generate_prompts(self, prompts: list[Prompt]) -> list[str]:
        return self.generate(prompts)

    async def async_generate(self, prompts: list[Prompt]) -> list[str]:
        # Validate the whole batch before sending any billable requests.
        for prompt in prompts:
            if not isinstance(prompt, Prompt):
                raise ValueError(
                    "Decision generation requires Prompt objects with decisions"
                )
            decisions = prompt.decisions
            if not decisions or len(decisions) < 2:
                raise ValueError(
                    f"Prompt {prompt.uuid} requires at least two decisions"
                )
            if any(
                not isinstance(label, str)
                or not label.strip()
                or not isinstance(description, str)
                or not description.strip()
                for label, description in decisions.items()
            ):
                raise ValueError(
                    "Decision labels and descriptions must be non-empty strings"
                )
        return await super().async_generate(prompts)

    async def _wait_for_request_slot(self) -> None:
        if self.requests_per_minute is None:
            return
        loop = asyncio.get_running_loop()
        if self._rate_limit_loop is not loop:
            # Synchronous generate() calls may create a new loop per batch.
            # Keep the monotonic deadline across loops, but recreate the lock.
            self._rate_limit_loop = loop
            self._rate_limit_lock = asyncio.Lock()
        async with self._rate_limit_lock:
            delay = self._next_request_at - time.monotonic()
            while delay > 0:
                await asyncio.sleep(delay)
                delay = self._next_request_at - time.monotonic()
            self._next_request_at = time.monotonic() + 60 / self.requests_per_minute

    async def call_generation_api(self, prompt: Prompt) -> str:
        await self._wait_for_request_slot()
        response = await self.client.post(
            "decisions",
            cast_to=dict[str, Any],
            body={
                "model": self.model,
                "state": {"prompt": prompt.text},
                "questions": {
                    "answer": {
                        "type": "choice",
                        "instructions": "Answer the question in state.prompt by selecting one of the provided choices.",
                        "criteria": prompt.decisions,
                    }
                },
            },
        )
        try:
            answer = response["answers"]["answer"]
            choice = answer["choice"]
            valid = answer["type"] == "choice" and choice in prompt.decisions
        except (KeyError, TypeError):
            valid = False
        if not valid:
            raise ValueError(
                "Decisions API did not return a valid choice for this prompt"
            )
        return choice
