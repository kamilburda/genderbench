"""
Find all the probe READMEs and create appropriate .rst files in the
docs/source/probes dir.

This file is supposed to be run from the docs/ dir.
"""
import glob
from pathlib import Path

for probe_readme_file in glob.glob("../src/gender_bench/probes/*/*/README.md"):
    path = Path(probe_readme_file)
    with open(f"source/probes/{path.parts[-2]}.rst", "w") as f:
        f.write(f".. mdinclude:: ../../{probe_readme_file}\n")