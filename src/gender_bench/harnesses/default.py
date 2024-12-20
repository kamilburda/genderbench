from gender_bench.harnesses.harness import Harness
from gender_bench.probes.affective.dreaddit.dreaddit_probe import DreadditProbe
from gender_bench.probes.affective.isear.isear_probe import IsearProbe
from gender_bench.probes.creative.gest_creative.gest_creative_probe import GestCreativeProbe
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
        recipe = {
            IsearProbe(): ["max_diff"],
            GestCreativeProbe(
                template=GestCreativeProbe.templates[0], num_repetitions=10
            ): ["stereotype_rate"],
            InventoriesProbe(
                template=InventoriesProbe.templates[0], num_repetitions=50
            ): ["stereotype_rate"],
            JobsLumProbe(template=JobsLumProbe.templates[2], num_repetitions=10): [
                "correlation"
            ],
            DiscriminationTamkinProbe(): [
                "max_diff",
            ],
            HiringAnProbe(sample_k=20_000): [
                "diff_acceptance_rate",
                "diff_correlation",
            ],
            HiringBloombergProbe(): [
                "software_engineer_masc_rate",
                "hr_specialist_masc_rate",
                "retail_masc_rate",
                "financial_analyst_masc_rate",
            ],
            DreadditProbe(num_repetitions=5): ["max_diff_tpr", "max_diff_tnr"],
            BbqProbe(): ["stereotypical_rate"],
            DirectProbe(num_repetitions=10): ["gest_fail_rate"],
            GestProbe(template=GestProbe.templates[1]): ["stereotype_rate"],
        }
        super().__init__(recipe=recipe, **kwargs)
