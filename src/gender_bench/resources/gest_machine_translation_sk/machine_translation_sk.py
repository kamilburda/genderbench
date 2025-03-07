import io

import pandas as pd
import requests

url_to_download = "https://github.com/kinit-sk/gest/raw/refs/heads/main/data/gender_variants.csv"
output_filename = "machine_translation_sk.csv"

response = requests.get(url_to_download)
dataset_str = response.content.decode("utf-8")

with io.StringIO(dataset_str) as dataset_file:
  df_dataset = pd.read_csv(dataset_file)

df_dataset_filtered = df_dataset.loc[
  (df_dataset["translator"] == "GoogleTranslate") & (df_dataset["language"] == "sk"), :].copy()
df_dataset_filtered = df_dataset_filtered.drop(["translator", "language", "stereotype"], axis=1)

df_dataset_filtered.to_csv(output_filename, index=False)
