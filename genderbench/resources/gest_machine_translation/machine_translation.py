import requests

url_to_download = "https://github.com/kinit-sk/gest/raw/refs/heads/main/data/gender_variants.csv"
output_filename = "gender_variants.csv"

response = requests.get(url_to_download)

with open(output_filename, 'w', encoding="utf-8") as dataset_file:
  dataset_file.write(response.text)
