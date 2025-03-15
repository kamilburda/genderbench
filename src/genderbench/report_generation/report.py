import json
import re
import uuid
from importlib.metadata import version
from typing import Type

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
    github_path = f"https://genderbench.readthedocs.io/latest/probes/{probe_name_snake_case}.html"
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


def render_visualization(log_files: list[str], model_names: list[str]) -> str:
    """
    Prepare an HTML render based on DefaultHarness log files. Models' names
    must also be provided.
    """

    experiment_results = dict()
    for model_name, log_file in zip(model_names, log_files):
        probe_results = [json.loads(line) for line in open(log_file)]
        probe_results = {result["class"]: result for result in probe_results}
        experiment_results[model_name] = probe_results

    global_table = [
        [model_name, *global_table_row(model_results)]
        for model_name, model_results in experiment_results.items()
    ]

    rendered_sections = {
        section_name: section_html(section_name, experiment_results)
        for section_name in chart_config
    }

    rendered_html = main_template.render(
        global_table=global_table,
        rendered_sections=rendered_sections,
        version=version("genderbench"),
    )

    return rendered_html


def create_report(
    output_file_path: str, log_files: list[str], model_names: list[str]
) -> str:
    """
    Save an HTML render based on DefaultHarness log files. Models' names
    must also be provided.
    """
    html = render_visualization(log_files, model_names)
    with open(output_file_path, "w") as f:
        f.write(html)
