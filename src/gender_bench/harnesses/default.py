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
from gender_bench.probing.harness import Harness


class DefaultHarness(Harness):

    def __init__(self, **kwargs):
        probes = [
            IsearProbe(),
            GestCreativeProbe(
                num_repetitions=4,
            ),
            InventoriesProbe(
                num_repetitions=5,
            ),
            JobsLumProbe(num_repetitions=5),
            DiscriminationTamkinProbe(num_repetitions=3),
            HiringAnProbe(sample_k=20_000),
            HiringBloombergProbe(),
            DreadditProbe(num_repetitions=2),
            BbqProbe(),
            DirectProbe(),
            GestProbe(),
        ]
        super().__init__(probes=probes, **kwargs)
