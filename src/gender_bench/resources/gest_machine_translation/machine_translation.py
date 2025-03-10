import io

import pandas as pd
import requests

url_to_download = "https://github.com/kinit-sk/gest/raw/refs/heads/main/data/gender_variants.csv"
output_filename = "machine_translation.csv"

response = requests.get(url_to_download)
dataset_str = response.content.decode("utf-8")

with io.StringIO(dataset_str) as dataset_file:
  df_dataset = pd.read_csv(dataset_file)

df_dataset = df_dataset.drop(["stereotype"], axis=1)

df_dataset.to_csv(output_filename, index=False)
