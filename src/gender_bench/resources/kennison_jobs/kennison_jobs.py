import importlib.resources
from typing import Dict

import pandas as pd


def create_kennison_jobs_dict() -> Dict[str, float]:
    package_dir = importlib.resources.files("gender_bench")
    with open(package_dir / "resources/kennison_jobs/kennison_jobs.csv") as csv_file:
        df = pd.read_csv(csv_file)
    df = df[df.is_occupation]
    return dict(zip(df.noun, (df.score_by_females + df.score_by_males) / 2))
