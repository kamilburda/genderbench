import json
import re
import uuid
from importlib.metadata import version
from statistics import mean
from typing import Type

import numpy as np
import pandas as pd
from jinja2 import Environment, PackageLoader

from genderbench.probes import (
    BbqProbe,
    BusinessVocabularyProbe,
    DirectProbe,
    DiscriminationTamkinProbe,
    DiversityMedQaProbe,
    DreadditProbe,
    GestCreativeProbe,
    GestProbe,
    HiringAnProbe,
    HiringBloombergProbe,
    InventoriesProbe,
    IsearProbe,
    JobsLumProbe,
    RelationshipLevyProbe,
)
from genderbench.probing.probe import Probe

env = Environment(loader=PackageLoader("genderbench", "report_generation"))
main_template = env.get_template("main.html")
canvas_template = env.get_template("canvas.html")

chart_config = {
    "decision": [
        (DiscriminationTamkinProbe, "max_diff"),
        (HiringAnProbe, "diff_acceptance_rate"),
        (HiringAnProbe, "diff_regression"),
        (HiringBloombergProbe, "masculine_rate"),
        (HiringBloombergProbe, "stereotype_rate"),
        (DiversityMedQaProbe, "diff_success_rate"),
    ],
    "creative": [
        (BusinessVocabularyProbe, "mean_diff"),
        (GestCreativeProbe, "stereotype_rate"),
        (InventoriesProbe, "stereotype_rate"),
        (JobsLumProbe, "stereotype_rate"),
        (GestCreativeProbe, "masculine_rate"),
        (InventoriesProbe, "masculine_rate"),
        (JobsLumProbe, "masculine_rate"),
    ],
    "opinion": [
        (DirectProbe, "fail_rate"),
        (RelationshipLevyProbe, "diff_success_rate"),
        (GestProbe, "stereotype_rate"),
        (BbqProbe, "stereotype_rate"),
    ],
    "affective": [
        (DreadditProbe, "max_diff_stress_rate"),
        (IsearProbe, "max_diff"),
    ],
    "mvf": [
        (DiscriminationTamkinProbe, "diff_mvf_success_rate"),
        (HiringAnProbe, "diff_acceptance_rate"),
        (HiringBloombergProbe, "masculine_rate"),
        (DiversityMedQaProbe, "diff_success_rate"),
        (JobsLumProbe, "masculine_rate"),
        (RelationshipLevyProbe, "diff_success_rate"),
    ],
}

metric_normalizations = [
    (DiscriminationTamkinProbe, "max_diff", None),
    (HiringAnProbe, "diff_acceptance_rate", lambda x: abs(x)),
    (HiringAnProbe, "diff_regression", lambda x: max(0, x) / 2),
    (HiringBloombergProbe, "masculine_rate", lambda x: abs(x - 0.5)),
    (HiringBloombergProbe, "stereotype_rate", lambda x: max(0, x)),
    (DiversityMedQaProbe, "diff_success_rate", lambda x: abs(x)),
    (BusinessVocabularyProbe, "mean_diff", lambda x: max(0, x)),
    (GestCreativeProbe, "stereotype_rate", lambda x: max(0, x)),
    (InventoriesProbe, "stereotype_rate", lambda x: max(0, x)),
    (JobsLumProbe, "stereotype_rate", lambda x: max(0, x)),
    (GestCreativeProbe, "masculine_rate", lambda x: abs(x - 0.5)),
    (InventoriesProbe, "masculine_rate", lambda x: abs(x - 0.5)),
    (JobsLumProbe, "masculine_rate", lambda x: abs(x - 0.5)),
    (DirectProbe, "fail_rate", None),
    (RelationshipLevyProbe, "diff_success_rate", lambda x: abs(x)),
    (GestProbe, "stereotype_rate", lambda x: max(0, x)),
    (BbqProbe, "stereotype_rate", None),
    (DreadditProbe, "max_diff_stress_rate", None),
    (IsearProbe, "max_diff", None),
]


def aggregate_marks(marks: list[int]) -> int:
    """
    Logic for mark aggregation. Currently we average the worst three results.
    """
    marks = [mark for mark in marks if isinstance(mark, int)]
    worst_3_avg = round(sum(sorted(marks)[-3:]) / 3)
    return max(worst_3_avg, max(marks) - 1)


def section_mark(section_name: str, model_results: dict) -> int:
    """
    Aggregate marks of a model for the specified section.
    """
    return aggregate_marks(
        [
            model_results[probe_class.__name__]["marks"][metric]["mark_value"]
            for probe_class, metric in chart_config[section_name]
        ]
    )


def global_table_row(model_results: dict) -> list[str]:
    """
    Prepare row of aggregated marks for a single model's results.
    """
    row = [
        section_mark(section_name, model_results)
        for section_name in ["decision", "creative", "opinion", "affective"]
    ]
    # row.append(aggregate_marks(row))
    row = [chr(mark + 65) for mark in row]
    return row


def prepare_chart_data(
    probe_class: Type[Probe], metric: str, experiment_results: dict
) -> dict:
    """
    Create a structure that is used to populate a single chart.
    """
    probe_name = probe_class.__name__
    probe_name_snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", probe_name).lower()
    probe_name_snake_case = probe_name_snake_case.rsplit("_", maxsplit=1)[0]
    github_path = (
        f"https://genderbench.readthedocs.io/latest/probes/{probe_name_snake_case}.html"
    )
    first_result = list(experiment_results.values())[0]
    return {
        "description": first_result[probe_name]["marks"][metric]["description"],
        "tags": first_result[probe_name]["marks"][metric]["harm_types"],
        "model_names": list(experiment_results.keys()),
        "ranges": first_result[probe_name]["marks"][metric]["mark_ranges"],
        "intervals": [
            results[probe_name]["marks"][metric]["metric_value"]
            for results in experiment_results.values()
        ],
        "probe": probe_name,
        "metric": metric,
        "path": github_path,
        "uuid": uuid.uuid4(),
    }


def section_html(section_name: str, experiment_results: dict) -> str:
    """
    Create HTML renders for all the charts from a section.
    """
    canvases_html = list()
    canvases_html = [
        canvas_template.render(
            data=prepare_chart_data(probe_class, metric, experiment_results)
        )
        for probe_class, metric in chart_config[section_name]
    ]
    return "".join(canvases_html)


def normalized_table_row(model_results):
    """
    Calculate normalized results for one model.
    """

    def normalize(value, function):
        if function is None:
            function = lambda x: x  # noqa
        if isinstance(value, float):
            return function(value)
        elif isinstance(value, list):
            return function(mean(value))

    return [
        normalize(
            model_results[probe_class.__name__]["metrics"][metric_name],
            normalization_function,
        )
        for probe_class, metric_name, normalization_function in metric_normalizations
    ]


def calculate_normalized_table(log_files: list[str], model_names: list[str]):
    experiment_results = load_experiment_results(log_files, model_names)
    return _calculate_normalized_table(experiment_results)


def _calculate_normalized_table(experiment_results):
    """
    Prepare DataFrame table with normalized results.
    """
    data = np.vstack(
        [
            np.array(normalized_table_row(model_results))
            for _, model_results in experiment_results.items()
        ]
    )

    columns = [
        f"{probe_class.__name__}.{metric_name}"
        for probe_class, metric_name, _ in metric_normalizations
    ]

    # Add "average" column
    columns.append("Average")
    data = np.hstack([data, np.mean(data, axis=1, keepdims=True)])

    return pd.DataFrame(data, index=experiment_results.keys(), columns=columns)


def normalized_table_column_marks_wrapper(experiment_results):
    """
    This is a wrapper for a function that is used to color the cells in the
    table with normalized results.
    """

    def normalized_table_column_marks(mark_series):
        try:
            probe, metric = re.search(
                r"<span>([^.]+)\.([^.]+)</span>", mark_series.name
            ).groups()
            marks = [
                experiment_results[model][probe]["marks"][metric]["mark_value"]
                for model in experiment_results
            ]
        except AttributeError:
            return [""] * len(mark_series)
        colors = [
            "rgb(40, 167, 69, 0.25)",
            "rgb(255, 193, 7, 0.25)",
            "rgb(253, 126, 20, 0.25)",
            "rgb(220, 53, 69, 0.25)",
        ]
        return [f"background-color: {colors[i]}" for i in marks]

    return normalized_table_column_marks


def render_visualization(experiment_results: dict) -> str:
    """
    Prepare an HTML render based on DefaultHarness log files. Models' names
    must also be provided.
    """

    global_table = [
        [model_name, *global_table_row(model_results)]
        for model_name, model_results in experiment_results.items()
    ]

    rendered_sections = {
        section_name: section_html(section_name, experiment_results)
        for section_name in chart_config
    }

    normalized_table = _calculate_normalized_table(experiment_results)
    normalized_table = normalized_table.rename(
        columns=lambda col: f"<span>{col}</span>"
    )
    normalized_table = (
        normalized_table.style.format(precision=3)
        .apply(normalized_table_column_marks_wrapper(experiment_results), axis=0)
        .to_html(table_attributes='class="normalized-table"')
    )

    rendered_html = main_template.render(
        global_table=global_table,
        rendered_sections=rendered_sections,
        normalized_table=normalized_table,
        version=version("genderbench"),
    )

    return rendered_html


def load_experiment_results(log_files: list[str], model_names: list[str]) -> dict:
    """
    Load results from JSON files into a dictionary.
    """
    experiment_results = dict()
    for model_name, log_file in zip(model_names, log_files):
        probe_results = [json.loads(line) for line in open(log_file)]
        probe_results = {result["class"]: result for result in probe_results}
        experiment_results[model_name] = probe_results
    return experiment_results


def create_report(
    output_file_path: str, log_files: list[str], model_names: list[str]
) -> str:
    """
    Save an HTML render based on DefaultHarness log files. Models' names
    must also be provided.
    """
    experiment_results = load_experiment_results(log_files, model_names)

    html = render_visualization(experiment_results)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(html)
