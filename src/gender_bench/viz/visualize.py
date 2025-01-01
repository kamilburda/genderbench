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

global_table = [
    ["Random Model", "A", "C", "B", "D", "A"],
]

with open("logs/logs/73027101-5258-4da4-8a04-ff835e19e6d6.jsonl") as f:
    for line in f:
        pass
last_line = json.loads(line)
last_line

with open("logs/logs/3e481b13-df01-4181-91c9-6f0e158866ab.jsonl") as f:
    for line in f:
        pass
last_line_2 = json.loads(line)


chart_data = {
    "decision_making": [
        (DiscriminationTamkinProbe, "max_diff"),
        (HiringAnProbe, "diff_acceptance_rate"),
        (HiringAnProbe, "diff_correlation"),
        (HiringBloombergProbe, "stereotype_rate"),
        (HiringBloombergProbe, "masculine_rate"),
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


def probe_data(probe_class, metric):
    probe_name = probe_class.__name__
    github_path = (
        "https://github.com/matus-pikuliak/gender_bench/tree/main/src/"
        + probe_class.__module__.rsplit(".", 1)[0].replace(".", "/")
    )
    return {
        "description": last_line["Marks"][probe_name][metric]["description"],
        "tags": last_line["Marks"][probe_name][metric]["harm_types"],
        "model_names": ["Random Model", "Random Model 2"],
        "ranges": last_line["Marks"][probe_name][metric]["mark_ranges"],
        "intervals": [
            last_line["Marks"][probe_name][metric]["value"],
            last_line_2["Marks"][probe_name][metric]["value"],
        ],
        "probe": probe_name,
        "metric": metric,
        "path": github_path,
    }


def section_canvases(section_name):
    canvases_html = list()
    for probe_class, metric in chart_data[section_name]:
        html = canvas_template.render(data=probe_data(probe_class, metric))
        canvases_html.append(html)
    return "".join(canvases_html)


rendered_sections = {
    section_name: section_canvases(section_name) for section_name in chart_data
}

rendered_html = main_template.render(
    global_table=global_table,
    rendered_sections=rendered_sections,
)
with open("logs/out.html", "w") as f:
    f.write(rendered_html)
