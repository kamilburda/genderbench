"""
This is the script that was used to create `stereotypes.txt` based on the
published csv files.
"""

import ast
import io
import tarfile

import pandas as pd
import requests

# URL of the file to be downloaded
url = "https://maartensap.com/social-bias-frames/SBIC.v2.tgz"
file_name = "SBIC.v2.tgz"

# Download the file and create a `tarfile` object
response = requests.get(url, stream=True)
fileobj = io.BytesIO(response.content)
tar = tarfile.open(fileobj=fileobj, mode="r:gz")

stereotypes = []

for split in ("dev", "trn", "tst"):

    csv_file = tar.extractfile(f"SBIC.v2.agg.{split}.csv")

    df = pd.read_csv(csv_file)

    # Quickly filter out empty `targetStereotype` fields
    df = df[df.targetStereotype != "[]"]

    # Filter only gender stereotypes
    df = df[df.targetCategory.str.contains("gender")]

    df.targetStereotype = df.targetStereotype.apply(ast.literal_eval)

    for stereotype_list in df.targetStereotype:
        for stereotype in stereotype_list:
            if len(stereotype) < 6:
                continue
            # `men ` has a following white space due to false positives
            if any(
                stereotype.startswith(gender)
                for gender in ("men ", "women", "trans", "nonbinary")
            ):
                # Handle inconsistent interpunction
                stereotype = stereotype.replace(".", "").replace("  ", " ")
                stereotypes.append(stereotype)

with open("stereotypes.txt", "w") as output_file:
    for stereotype in sorted(set(stereotypes)):
        output_file.write(stereotype + "\n")
