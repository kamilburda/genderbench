from gender_bench.harnesses.harness import Harness
from gender_bench.probes.affective.dreaddit.dreaddit_probe import DreadditProbe
from gender_bench.probes.affective.isear.isear_probe import IsearProbe
from gender_bench.probes.creative.gest_creative.gest_creative_probe import (
    GestCreativeProbe,
)
from gender_bench.probes.creative.inventories.inventories_probe import InventoriesProbe
from gender_bench.probes.creative.jobs_lum.jobs_lum_probe import JobsLumProbe
from gender_bench.probes.decision_making.discrimination_tamkin.discrimination_tamkin_probe import (
    DiscriminationTamkinProbe,
)
from gender_bench.probes.decision_making.hiring_an.hiring_an_probe import HiringAnProbe
from gender_bench.probes.decision_making.hiring_bloomberg.hiring_bloomberg_probe import (
    HiringBloombergProbe,
)
from gender_bench.probes.opinion.bbq.bbq_probe import BbqProbe
from gender_bench.probes.opinion.direct.direct_probe import DirectProbe
from gender_bench.probes.opinion.gest.gest_probe import GestProbe


class DefaultHarness(Harness):

    def __init__(self, **kwargs):
        probes = [
            IsearProbe(),
            GestCreativeProbe(
                template=GestCreativeProbe.templates[0], num_repetitions=10
            ),
            InventoriesProbe(
                template=InventoriesProbe.templates[0], num_repetitions=50
            ),
            JobsLumProbe(template=JobsLumProbe.templates[2], num_repetitions=10),
            DiscriminationTamkinProbe(),
            HiringAnProbe(sample_k=20_000),
            HiringBloombergProbe(),
            DreadditProbe(num_repetitions=5),
            BbqProbe(),
            DirectProbe(num_repetitions=10),
            GestProbe(template=GestProbe.templates[1]),
        ]
        super().__init__(probes=probes, **kwargs)
