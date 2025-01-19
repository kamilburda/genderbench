from gender_bench.generators.random_generator import RandomGenerator
from gender_bench.probes import (
    BbqProbe,
    DirectProbe,
    DiscriminationTamkinProbe,
    DreadditProbe,
    GestCreativeProbe,
    GestProbe,
    HiringAnProbe,
    HiringBloombergProbe,
    InventoriesProbe,
    IsearProbe,
    JobsLumProbe,
)
from gender_bench.probes.opinion.gest.gest_templates import GestTemplate1


def test_isear():
    probe = IsearProbe(calculate_cis=False)
    generator = RandomGenerator(probe.emotions)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["max_diff"]) < 0.03


def test_gest_creative():
    generator = RandomGenerator(["she", "he", "..."])
    probe = GestCreativeProbe(
        template=GestCreativeProbe.templates[0], num_repetitions=10, calculate_cis=False
    )
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["stereotype_rate"]) < 0.03
    assert abs(probe.metrics["masculine_rate"] - 1 / 2) < 0.03


def test_inventories():
    generator = RandomGenerator(["she", "he", "..."])
    probe = InventoriesProbe(
        template=InventoriesProbe.templates[0], num_repetitions=100, calculate_cis=False
    )
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["stereotype_rate"]) < 0.05
    assert abs(probe.metrics["masculine_rate"] - 1 / 2) < 0.03


def test_jobs_lum():
    generator = RandomGenerator(["she", "he", "..."])
    probe = JobsLumProbe(
        template=JobsLumProbe.templates[0], num_repetitions=100, calculate_cis=False
    )
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["stereotype_rate"]) < 0.03
    assert abs(probe.metrics["masculine_rate"] - 1 / 2) < 0.03


def test_discrimination_tamkin():
    generator = RandomGenerator(["yes", "no", "..."])
    probe = DiscriminationTamkinProbe(calculate_cis=False)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["max_diff"]) < 0.03
    assert abs(probe.metrics["male_success_rate"] - 1 / 2) < 0.03


def test_hiring_an():
    generator = RandomGenerator(
        ["regret to inform you", "you have been selected", "..."]
    )
    probe = HiringAnProbe(sample_k=20_000, calculate_cis=False)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["diff_acceptance_rate"]) < 0.03
    assert abs(probe.metrics["diff_correlation"]) < 0.03


def test_hiring_bloomberg():
    generator = RandomGenerator(["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "..."])
    probe = HiringBloombergProbe(calculate_cis=False)
    probe.names = {
        "A1": ("male", "asian"),
        "A2": ("male", "asian"),
        "A3": ("male", "asian"),
        "A4": ("male", "asian"),
        "B1": ("female", "asian"),
        "B2": ("female", "asian"),
        "B3": ("female", "asian"),
        "B4": ("female", "asian"),
    }
    probe.races = ["asian"]
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["masculine_rate"] - 0.5) < 0.03
    assert abs(probe.metrics["stereotype_rate"]) < 0.03


def test_dreaddit():
    generator = RandomGenerator(["yes", "no", "..."])
    probe = DreadditProbe(num_repetitions=5, calculate_cis=False)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["max_diff_tpr"]) < 0.03
    assert abs(probe.metrics["max_diff_tnr"]) < 0.03


def test_bbq():
    generator = RandomGenerator(["(a)", "(b)", "(c)", "..."])
    probe = BbqProbe(calculate_cis=False)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["stereotype_rate"] - 1 / 3) < 0.03
    assert abs(probe.metrics["logical_rate"] - 1 / 3) < 0.03


def test_direct():
    generator = RandomGenerator(["yes", "no", "..."])
    probe = DirectProbe(num_repetitions=10, calculate_cis=False)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["sbic_fail_rate"] - 1 / 2) < 0.03


def test_gest():
    generator = RandomGenerator(["(a)", "(b)", "(c)", "..."])
    probe = GestProbe(template=GestTemplate1, calculate_cis=False)
    probe.run(generator)
    print(probe.__class__, probe.metrics, end="\n\n")
    assert abs(probe.metrics["stereotype_rate"]) < 0.03
    assert abs(probe.metrics["frequency_male_option"] - 1 / 4) < 0.03


def test_marks():
    generator = RandomGenerator(["(a)", "(b)", "(c)", "..."])
    probe = GestProbe(template=GestTemplate1, calculate_cis=False)
    probe.run(generator)
    assert probe.marks["stereotype_rate"]["mark_value"] == 0

    probe = BbqProbe(calculate_cis=True)
    probe.run(generator)
    assert probe.marks["stereotype_rate"]["mark_value"] == 2
