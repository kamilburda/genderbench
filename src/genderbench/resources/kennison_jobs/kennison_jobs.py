import importlib.resources

import pandas as pd


def create_kennison_jobs_dict() -> dict[str, float]:
    package_dir = importlib.resources.files("genderbench")
    with open(package_dir / "resources/kennison_jobs/kennison_jobs.csv") as csv_file:
        df = pd.read_csv(csv_file)
    return dict(zip(df.noun, df.score))
