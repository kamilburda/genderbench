import collections
import json
import re
import uuid
from importlib.metadata import version
from statistics import mean
from typing import Type

import numpy as np
import pandas as pd
from jinja2 import Environment, PackageLoader, Template

from genderbench.probing.probe import Probe

env = Environment(loader=PackageLoader("genderbench", "report_generation"))

DEFAULT_MAIN_TEMPLATE = env.get_template("main.html")
DEFAULT_CANVAS_TEMPLATE = env.get_template("canvas.html")


def _create_chart_config():
    all_subclasses: list[Probe] = []
    current_subclasses = Probe.__subclasses__()

    unique_classes = set()

    while current_subclasses:
        subclass = current_subclasses.pop(0)

        # This is used to prevent errors in pandas dataframes in case dynamic
        # classes with the same name were created multiple times.
        subclass_path = f'{subclass.__module__}{subclass.__qualname__}'
        if subclass_path in unique_classes:
            continue

        unique_classes.add(subclass_path)
        all_subclasses.append(subclass)
        current_subclasses.extend(subclass.__subclasses__())

    all_subclasses.sort(key=lambda subclass: subclass.__name__)

    chart_config = collections.defaultdict(list)
    for subclass in all_subclasses:
        for mark_definition in subclass.mark_definitions:
            for harm_type in mark_definition.harm_types:
                value = (subclass, mark_definition.metric_name)
                chart_config[harm_type].append(value)
                chart_config["all"].append(value)
    
    return chart_config


chart_config = _create_chart_config()


def section_emojis(section_name: str, model_results: dict) -> int:
    """
    Return an emoji string for a model and a section.
    """
    emojis = "🟩🟨🟧🟥"
    marks = [
        model_results[probe_class.__name__]["marks"][metric]["mark_value"]
        for probe_class, metric in chart_config[section_name]
        if probe_class.__name__ in model_results and metric in model_results[probe_class.__name__]["marks"]
    ]
    marks = sorted(mark for mark in marks if isinstance(mark, int))
    return "".join(emojis[mark] for mark in marks)


def emoji_table_row(model_results: dict, section_names: list[str]) -> list[str]:
    """
    Return emoji strings for a model and a list of sections.
    """
    return [
        section_emojis(section_name, model_results) for section_name in section_names
    ]


def prepare_chart_data(
    probe_class: Type[Probe], metric_name: str, experiment_results: dict
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
    mark_definition = next(
        md for md in probe_class.mark_definitions if md.metric_name == metric_name
    )
    return {
        "description": mark_definition.description,
        "model_names": list(experiment_results.keys()),
        "ranges": {
            k: list(map(list, v)) for k, v in mark_definition.mark_ranges.items()
        },
        "intervals": [
            results[probe_name]["marks"][metric_name]["metric_value"]
            for results in experiment_results.values()
        ],
        "probe": probe_name,
        "metric": metric_name,
        "path": github_path,
        "uuid": uuid.uuid4(),
    }


def section_html(section_name: str, experiment_results: dict, canvas_template: Template) -> str:
    """
    Create HTML renders for all the charts from a section.
    """
    canvases_html = list()
    canvases_html = [
        canvas_template.render(
            data=prepare_chart_data(probe_class, metric_name, experiment_results)
        )
        for probe_class, metric_name in chart_config[section_name]
        if _is_probe_and_metric_in_experiment_results(probe_class, metric_name, experiment_results)
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

    rows = []
    for section in (
        "outcome_disparity",
        "stereotypical_reasoning",
        "representational_harms",
    ):
        for probe_class, metric_name in chart_config[section]:
            if (probe_class.__name__ not in model_results
                or metric_name not in model_results[probe_class.__name__]["marks"]):
                continue

            normalization_function = _find_metric_normalization(probe_class, metric_name)
            row = normalize(
                model_results[probe_class.__name__]["metrics"][metric_name],
                normalization_function,
            )
            rows.append(row)
    return rows


def calculate_normalized_table(experiment_results):
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
        f"{probe_class.__name__.replace("Probe", "")}.{metric_name}"
        for section in (
            "outcome_disparity",
            "stereotypical_reasoning",
            "representational_harms",
        )
        for probe_class, metric_name in chart_config[section]
        if _is_probe_and_metric_in_experiment_results(probe_class, metric_name, experiment_results)
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
                experiment_results[model][probe + "Probe"]["marks"][metric][
                    "mark_value"
                ]
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

        mark_colors = []
        for i in marks:
            try:
                color = colors[i]
            except Exception:
                mark_colors.append(f"")
            else:
                mark_colors.append(f"background-color: {color}")

        return mark_colors

    return normalized_table_column_marks


def render_visualization(experiment_results: dict, main_template: Template, canvas_template: Template) -> str:
    """
    Prepare an HTML render based on DefaultHarness log files. Models' names
    must also be provided.
    """

    emoji_table_1 = [
        [
            model_name,
            *emoji_table_row(
                model_results,
                [
                    "outcome_disparity",
                    "stereotypical_reasoning",
                    "representational_harms",
                ],
            ),
        ]
        for model_name, model_results in experiment_results.items()
    ]
    emoji_table_2 = [
        [model_name, *emoji_table_row(model_results, ["all"])]
        for model_name, model_results in experiment_results.items()
    ]

    rendered_sections = {
        section_name: section_html(section_name, experiment_results, canvas_template)
        for section_name in chart_config
    }

    normalized_table = calculate_normalized_table(experiment_results)
    normalized_table = normalized_table.rename(
        columns=lambda col: f"<span>{col}</span>"
    )
    normalized_table = (
        normalized_table.style.format(precision=3)
        .apply(normalized_table_column_marks_wrapper(experiment_results), axis=0)
        .to_html(table_attributes='class="normalized-table"')
    )

    rendered_html = main_template.render(
        emoji_table_1=emoji_table_1,
        emoji_table_2=emoji_table_2,
        rendered_sections=rendered_sections,
        normalized_table=normalized_table,
        version=version("genderbench"),
    )

    return rendered_html


def load_experiment_results(
        log_files: list[str],
        model_names: list[str],
        metric_names_to_ignore: list[str] | None = None,
) -> dict:
    """
    Load results from JSON files into a dictionary.
    """
    if metric_names_to_ignore is None:
        metric_names_to_ignore = []

    experiment_results = dict()
    for model_name, log_file in zip(model_names, log_files):
        probe_results = [json.loads(line) for line in open(log_file)]

        processed_probe_results = {}
        for result in probe_results:
            processed_probe_results[result["class"]] = result
            for metric_name in metric_names_to_ignore:
                result["marks"].pop(metric_name, None)

        experiment_results[model_name] = processed_probe_results
    return experiment_results


def create_report(
    output_file_path: str,
    log_files: list[str],
    model_names: list[str],
    main_template: Template | None = None,
    canvas_template: Template | None = None,
    metric_names_to_ignore: list[str] | None = None,
) -> str:
    """
    Save an HTML render based on DefaultHarness log files. Models' names
    must also be provided.
    """
    if main_template is None:
        main_template = DEFAULT_MAIN_TEMPLATE

    if canvas_template is None:
        canvas_template = DEFAULT_CANVAS_TEMPLATE

    experiment_results = load_experiment_results(
        log_files, model_names, metric_names_to_ignore)

    html = render_visualization(experiment_results, main_template, canvas_template)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(html)


def _is_probe_and_metric_in_experiment_results(probe_class, metric_name, experiment_results):
    probe_name = probe_class.__name__
    return all(
        (probe_name in results_per_model
         and metric_name in results_per_model[probe_name]["marks"])
        for results_per_model in experiment_results.values()
    )


def _find_metric_normalization(probe_class: Probe, metric_name: str):
    for mark_definition in probe_class.mark_definitions:
        if mark_definition.metric_name == metric_name:
            return mark_definition.metric_normalization

    return None
