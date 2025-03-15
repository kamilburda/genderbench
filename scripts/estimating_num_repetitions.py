"""
This script shows an example of how it is possible to increase `num_repetitions`
one by one. This can be used to make judgments about the optimal value of
repetitions for individual probes, i.e., you can obsereve the range of the CI
interval `mx-mn` and see how it changes when the number of repetitions is
increased.

It is not recommended to use `RandomGenerator` for this use case as it does not
simulate real LM distribution.
"""

from genderbench.generators.random import RandomGenerator
from genderbench.probes.gest.gest_probe import GestProbe
from genderbench.probing.probe import status


def probe_factory():
    return GestProbe(
        template=GestProbe.templates[0],
        num_reorderings=1,
        calculate_cis=True,
    )


generator = RandomGenerator(["(a)", "(b)", "(c)"])

metric_of_interest = "stereotype_rate"

main_probe = probe_factory()

assert main_probe.calculate_cis

main_probe.run(generator)
mn, mx = main_probe.metrics[metric_of_interest]
print("Reps=1", mn, mx, mx - mn)

for i in range(10):

    new_probe = probe_factory()
    new_probe.calculate_cis = False
    new_probe.run(generator)
    for main_item, new_item in zip(main_probe.probe_items, new_probe.probe_items):
        for attempt in new_item.attempts:
            attempt.repetition_id = i + 1
            main_item.attempts.append(attempt)

    del new_probe

    main_item.num_repetitions += 1
    main_probe.status = status.EVALUATED

    # Clear cache in case metric calculator uses it
    obj = main_probe.metric_calculator
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if callable(attr) and hasattr(attr, "cache_clear"):
            attr.cache_clear()

    main_probe.calculate_metrics()

    mn, mx = main_probe.metrics[metric_of_interest]
    print(f"Reps={i + 2}", mn, mx, mx - mn)
