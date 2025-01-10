from gender_bench.harnesses.harness import Harness
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


class DefaultHarness(Harness):

    def __init__(self, **kwargs):
        probes = [
            IsearProbe(),
            GestCreativeProbe(
                template=GestCreativeProbe.templates[0], num_repetitions=5
            ),
            InventoriesProbe(template=InventoriesProbe.templates[0], num_repetitions=5),
            JobsLumProbe(template=JobsLumProbe.templates[2], num_repetitions=5),
            DiscriminationTamkinProbe(),
            HiringAnProbe(sample_k=20_000),
            HiringBloombergProbe(),
            DreadditProbe(num_repetitions=3),
            BbqProbe(),
            DirectProbe(num_repetitions=5),
            GestProbe(template=GestProbe.templates[1]),
        ]
        super().__init__(probes=probes, **kwargs)
