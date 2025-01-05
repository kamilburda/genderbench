import json

from jinja2 import Environment, PackageLoader

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

env = Environment(loader=PackageLoader("gender_bench", "viz"))
main_template = env.get_template("main.html")
canvas_template = env.get_template("canvas.html")


chart_data = {
    "decision_making": [
        (DiscriminationTamkinProbe, "max_diff"),
        (HiringAnProbe, "diff_acceptance_rate"),
        (HiringAnProbe, "diff_correlation"),
        (HiringBloombergProbe, "masculine_rate"),
        (HiringBloombergProbe, "stereotype_rate"),
    ],
    "creative": [
        (GestCreativeProbe, "stereotype_rate"),
        (InventoriesProbe, "stereotype_rate"),
        (JobsLumProbe, "stereotype_rate"),
        (GestCreativeProbe, "masculine_rate"),
        (InventoriesProbe, "masculine_rate"),
        (JobsLumProbe, "masculine_rate"),
    ],
    "opinion": [
        (DirectProbe, "fail_rate"),
        (GestProbe, "stereotype_rate"),
        (BbqProbe, "stereotype_rate"),
    ],
    "affective": [
        (DreadditProbe, "max_diff_stress_rate"),
        (IsearProbe, "max_diff"),
    ],
}


def aggregate_marks(marks: list[int]):
    marks = [mark for mark in marks if isinstance(mark, int)]
    return round(sum(sorted(marks)[-3:]) / 3)


def section_mark(section_name, model_results):
    return aggregate_marks(
        [
            model_results["Marks"][probe_class.__name__][metric]["mark"]
            for probe_class, metric in chart_data[section_name]
        ]
    )


def global_table_row(model_results):
    row = [section_mark(section_name, model_results) for section_name in chart_data]
    row.append(aggregate_marks(row))
    row = [chr(mark + 65) for mark in row]
    return row


def probe_data(probe_class, metric, logged_results):
    probe_name = probe_class.__name__
    github_path = (
        "https://github.com/matus-pikuliak/gender_bench/tree/main/src/"
        + probe_class.__module__.rsplit(".", 1)[0].replace(".", "/")
    )
    first_result = list(logged_results.values())[0]
    return {
        "description": first_result["Marks"][probe_name][metric]["description"],
        "tags": first_result["Marks"][probe_name][metric]["harm_types"],
        "model_names": list(logged_results.keys()),
        "ranges": first_result["Marks"][probe_name][metric]["mark_ranges"],
        "intervals": [
            results["Marks"][probe_name][metric]["value"]
            for results in logged_results.values()
        ],
        "probe": probe_name,
        "metric": metric,
        "path": github_path,
    }


def section_canvases(section_name, logged_results):
    canvases_html = list()
    for probe_class, metric in chart_data[section_name]:
        html = canvas_template.render(
            data=probe_data(probe_class, metric, logged_results)
        )
        canvases_html.append(html)
    return "".join(canvases_html)


def create_visualizations(log_files, model_names):

    logged_results = {
        model_name: json.loads(open(log_file).readlines()[-1])
        for model_name, log_file in zip(model_names, log_files)
    }

    global_table = [
        [model_name, *global_table_row(model_results)]
        for model_name, model_results in logged_results.items()
    ]

    rendered_sections = {
        section_name: section_canvases(section_name, logged_results)
        for section_name in chart_data
    }

    rendered_html = main_template.render(
        global_table=global_table,
        rendered_sections=rendered_sections,
    )
    with open("logs/out.html", "w") as f:
        f.write(rendered_html)


if __name__ == "__main__":
    logfiles = [
        "logs/logs/87d269c2-a165-4599-a6d4-e36ed3ad590a.jsonl",
        "logs/logs/a96da985-a48f-4e3b-934d-b26d904e6f9f.jsonl",
        "logs/logs/65901fba-b50e-4460-8c0c-1517c3a54f51.jsonl",
    ]
    model_names = [
        "Random 1",
        "Random 2",
        "Random 3",
    ]
    create_visualizations(log_files=logfiles, model_names=model_names)
