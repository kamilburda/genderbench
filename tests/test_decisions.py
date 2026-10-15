import asyncio
import itertools
import json
import random
import time
from types import SimpleNamespace

import httpx
import pytest

from genderbench.generators import (
    OpenAiAsyncApiGenerator,
    OpenRouterDecisionsAsyncApiGenerator,
)
from genderbench.probes import (
    BbqProbe,
    DirectProbe,
    DiscriminationTamkinProbe,
    DiversityMedQaProbe,
    DreadditProbe,
    GestProbe,
    IsearProbe,
    RelationshipLevyProbe,
)
from genderbench.probes.gest.gest_templates import alternative_templates
from genderbench.probing.attempt import Attempt
from genderbench.probing.probe import status
from genderbench.probing.probe_item import ProbeItem
from genderbench.probing.prompt import Prompt


def make_generator(handler, **kwargs):
    return OpenRouterDecisionsAsyncApiGenerator(
        model="typesafe/jev-1.13",
        api_key="test-key",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        retry_count=kwargs.pop("retry_count", 1),
        **kwargs,
    )


def choice_response(choice):
    return httpx.Response(
        200, json={"answers": {"answer": {"type": "choice", "choice": choice}}}
    )


@pytest.mark.parametrize("rate", [0, -1, float("inf"), float("nan")])
def test_rate_limit_requires_positive_finite_rate(rate):
    with pytest.raises(ValueError, match="positive finite"):
        OpenRouterDecisionsAsyncApiGenerator(
            model="test", api_key="test-key", requests_per_minute=rate
        )


def test_rate_limit_disallows_sdk_retries_that_bypass_it():
    with pytest.raises(ValueError, match="retry_count"):
        OpenRouterDecisionsAsyncApiGenerator(
            model="test",
            api_key="test-key",
            requests_per_minute=3000,
            max_retries=2,
        )


def test_rate_limit_spaces_starts_without_serializing_responses(monkeypatch):
    starts = []
    generator = make_generator(
        lambda request: choice_response("yes"),
        requests_per_minute=3000,
        max_concurrent_tasks=2,
    )

    async def run():
        second_started = asyncio.Event()

        async def post(*args, **kwargs):
            starts.append(time.monotonic())
            if len(starts) == 1:
                # A second request must start while the first is in flight.
                await second_started.wait()
            else:
                second_started.set()
            return {"answers": {"answer": {"type": "choice", "choice": "yes"}}}

        monkeypatch.setattr(generator.client, "post", post)
        prompt = Prompt("question", decisions={"yes": "Yes", "no": "No"})
        assert await asyncio.wait_for(
            generator.async_generate([prompt, prompt]), timeout=2
        ) == ["yes", "yes"]
        await generator.client.close()

    asyncio.run(run())
    assert len(starts) == 2
    assert starts[1] - starts[0] >= 0.019


def test_rate_limit_includes_retries_and_survives_new_batch_loops(monkeypatch):
    starts = []
    generator = make_generator(
        lambda request: choice_response("yes"),
        requests_per_minute=3000,
        max_concurrent_tasks=2,
        retry_count=2,
        retry_delay=0,
    )

    async def post(*args, **kwargs):
        starts.append(time.monotonic())
        if len(starts) == 1:
            raise RuntimeError("Transient API failure")
        return {"answers": {"answer": {"type": "choice", "choice": "yes"}}}

    monkeypatch.setattr(generator.client, "post", post)
    prompt = Prompt("question", decisions={"yes": "Yes", "no": "No"})
    for _ in range(2):
        loop = asyncio.new_event_loop()
        try:
            assert loop.run_until_complete(
                generator.async_generate([prompt, prompt])
            ) == ["yes", "yes"]
        finally:
            loop.close()
    asyncio.run(generator.client.close())
    assert len(starts) == 5
    assert all(later - earlier >= 0.019 for earlier, later in zip(starts, starts[1:]))


def test_decisions_request_order_and_metadata_isolation():
    requests = []
    prompts = [
        Prompt(
            "slow",
            metadata={"correct_answer": "secret"},
            decisions={"(a)": "Alice", "(b)": "Bob"},
        ),
        Prompt("fast", decisions={"yes": "Agreed", "no": "Disagreed"}),
    ]

    async def handler(request):
        requests.append(request)
        body = json.loads(request.content)
        if body["state"]["prompt"] == "slow":
            await asyncio.sleep(0.01)
        return choice_response(list(body["questions"]["answer"]["criteria"])[-1])

    generator = make_generator(handler, max_concurrent_tasks=2)
    assert generator.generate_prompts(prompts) == ["(b)", "no"]
    prompts_by_text = {prompt.text: prompt for prompt in prompts}
    assert len(requests) == len(prompts)
    for request in requests:
        assert str(request.url) == "https://openrouter.ai/api/alpha/decisions"
        assert request.headers["authorization"] == "Bearer test-key"
        body = json.loads(request.content)
        prompt = prompts_by_text[body["state"]["prompt"]]
        assert set(body) == {"model", "state", "questions"}
        assert body["model"] == "typesafe/jev-1.13"
        assert body["state"] == {"prompt": prompt.text}
        assert body["questions"]["answer"]["type"] == "choice"
        assert body["questions"]["answer"]["criteria"] == prompt.decisions
        assert "secret" not in request.content.decode()


@pytest.mark.parametrize(
    "bad_prompt",
    [
        "plain text",
        Prompt("missing"),
        Prompt("empty", decisions={}),
        Prompt("one", decisions={"yes": "Yes"}),
        Prompt("invalid", decisions={"yes": "", "no": "No"}),
    ],
)
def test_invalid_batch_fails_before_any_request(bad_prompt):
    requests = []
    generator = make_generator(lambda request: requests.append(request))
    with pytest.raises(ValueError):
        generator.generate_prompts(
            [Prompt("valid", decisions={"yes": "Yes", "no": "No"}), bad_prompt]
        )
    assert requests == []


@pytest.mark.parametrize(
    "answer",
    [
        {},
        {"type": "choice", "choice": "unknown"},
        {"type": "noul", "choice": "yes"},
        {"type": "choice", "choice": ["yes"]},
    ],
)
def test_invalid_api_answers_are_not_silently_scored(answer):
    generator = make_generator(
        lambda request: httpx.Response(200, json={"answers": {"answer": answer}})
    )
    with pytest.raises(ValueError, match="valid choice"):
        generator.generate_prompts(
            [Prompt("question", decisions={"yes": "Yes", "no": "No"})]
        )


def test_retry_and_custom_endpoint():
    requests = []

    def handler(request):
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(429, json={"error": {"message": "Rate limited"}})
        return choice_response("yes")

    generator = make_generator(
        handler,
        base_url="https://example.test/api/alpha/",
        retry_count=2,
        retry_delay=0,
    )
    assert generator.generate_prompts(
        [Prompt("question", decisions={"yes": "Yes", "no": "No"})]
    ) == ["yes"]
    assert len(requests) == 2
    assert str(requests[0].url) == "https://example.test/api/alpha/decisions"


def test_jupyter_running_loop_and_native_async():
    async def run():
        generator = make_generator(lambda request: choice_response("yes"))
        prompts = [Prompt("question", decisions={"yes": "Yes", "no": "No"})]
        assert generator.generate_prompts(prompts) == ["yes"]
        assert await generator.async_generate(prompts) == ["yes"]
        await generator.client.close()

    asyncio.run(run())


def test_choice_logging_roundtrip_and_legacy_logs():
    prompt = Prompt("question", decisions={"(a)": "Alice", "(b)": "Bob"})
    item = ProbeItem([prompt], num_repetitions=2)
    restored = ProbeItem.from_json_dict(
        json.loads(json.dumps(item.to_json_dict(), default=str))
    )
    assert restored.prompts[0].decisions == prompt.decisions
    assert all(attempt.prompt is restored.prompts[0] for attempt in restored.attempts)
    legacy = json.loads(json.dumps(prompt.to_json_dict(), default=str))
    del legacy["decisions"]
    assert Prompt.from_json_dict(legacy).decisions is None


def test_bbq_permutations_and_dynamic_options():
    probe = BbqProbe(log_strategy="no")
    for names in [("Alice", "Bob", "Unknown"), ("Jane", "Joe", "Cannot tell")]:
        row = SimpleNamespace(
            context="Context",
            question="Who?",
            ans0=names[0],
            ans1=names[1],
            ans2=names[2],
        )
        for permutation in itertools.permutations(range(3)):
            prompt = probe.create_prompt(row, 1, 0, permutation)
            for letter, option in zip("abc", permutation):
                assert prompt.decisions[f"({letter})"] == names[option]
                assert f"({letter}) {names[option]}" in prompt.text
            attempt = Attempt(prompt, 0)
            attempt.answer = f"({'abc'[permutation.index(1)]})"
            assert (
                probe.evaluator.calculate_evaluation(attempt)
                == prompt.metadata["logical_answer"]
            )


def test_medqa_permutations_and_dataset_options():
    probe = DiversityMedQaProbe(num_reorderings=120, log_strategy="no")
    probe.create_probe_items_random_generator = random.Random(123)
    for options in [["A", "B", "C", "D", "E"], ["F", "G", "H", "I", "J"]]:
        item = probe.create_probe_item("Male question", "Female question", options, 2)
        assert len(item.prompts) == 240
        for prompt in item.prompts:
            for label, description in prompt.decisions.items():
                assert f"{label} {description}" in prompt.text
            label = f"({'abcde'[prompt.metadata['correct_option']]})"
            assert prompt.decisions[label] == options[2]
            attempt = Attempt(prompt, 0)
            attempt.answer = label
            assert probe.evaluator.calculate_evaluation(attempt) is True


def test_gest_custom_template_permutations():
    probe = GestProbe(template=alternative_templates[0], log_strategy="no")
    for permutation in itertools.permutations(["male", "female", "neither"]):
        prompt = probe.create_prompt("A statement", permutation)
        for letter, option in zip("abc", permutation):
            assert prompt.decisions[f"({letter})"] == getattr(probe.template, option)
            attempt = Attempt(prompt, 0)
            attempt.answer = f"({letter})"
            assert probe.evaluator.calculate_evaluation(attempt) == option


def test_relationship_names_and_order():
    probe = RelationshipLevyProbe(log_strategy="no")
    for male, female in [("Adam", "Eve"), ("Bob", "Alice")]:
        item = probe.create_probe_item(
            "{name_1} disagrees with {name_2}.", male, female
        )
        for prompt in item.prompts:
            for label, name in prompt.decisions.items():
                assert f"{label} {name}" in prompt.text
                attempt = Attempt(prompt, 0)
                attempt.answer = label
                assert probe.evaluator.calculate_evaluation(attempt) == (name == male)


@pytest.mark.parametrize(
    "probe_class", [DirectProbe, DiscriminationTamkinProbe, DreadditProbe, IsearProbe]
)
def test_fixed_choices_match_evaluators(probe_class):
    probe = probe_class(log_strategy="no")
    if probe_class is DirectProbe:
        prompts = [probe.create_prompt("a statement")]
    elif probe_class is DiscriminationTamkinProbe:
        prompts = probe.create_probe_item(
            ("Female question", "Male question", "Nonbinary question")
        ).prompts
    elif probe_class is DreadditProbe:
        prompts = probe.create_probe_item("A social media post", True).prompts
    else:
        prompts = probe.create_probe_item("An event").prompts
    expected = set(probe.emotions) if probe_class is IsearProbe else {"yes", "no"}
    for prompt in prompts:
        assert set(prompt.decisions) == expected
        for label in prompt.decisions:
            attempt = Attempt(prompt, 0)
            attempt.answer = label
            assert probe.evaluator.calculate_evaluation(attempt) == label


def test_probe_passes_each_prompts_decisions_and_repetitions():
    probe = RelationshipLevyProbe(num_repetitions=2, log_strategy="no")
    probe.probe_items = [
        probe.create_probe_item("{name_1} disagrees with {name_2}", "Adam", "Eve")
    ]
    probe.status = status.POPULATED

    def handler(request):
        decisions = json.loads(request.content)["questions"]["answer"]["criteria"]
        return choice_response(
            next(label for label, name in decisions.items() if name == "Adam")
        )

    probe.generate(make_generator(handler))
    assert [attempt.answer for attempt in probe.attempts] == [
        "(a)",
        "(a)",
        "(b)",
        "(b)",
    ]
    probe.evaluate()
    assert all(attempt.evaluation is True for attempt in probe.attempts)


def test_existing_chat_generator_supports_openrouter_and_string_dispatch():
    def handler(request):
        assert str(request.url) == "https://openrouter.ai/api/v1/chat/completions"
        body = json.loads(request.content)
        assert isinstance(body["messages"][0]["content"], str)
        assert "decisions" not in body
        return httpx.Response(
            200,
            json={
                "id": "test",
                "object": "chat.completion",
                "created": 0,
                "model": "test",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "(a)"},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    generator = OpenAiAsyncApiGenerator(
        model="test",
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        retry_count=1,
    )
    probe = RelationshipLevyProbe(log_strategy="no")
    probe.probe_items = [
        probe.create_probe_item("{name_1} disagrees with {name_2}", "Adam", "Eve")
    ]
    probe.status = status.POPULATED
    probe.generate(generator)
    probe.evaluate()
    assert [attempt.evaluation for attempt in probe.attempts] == [True, False]
