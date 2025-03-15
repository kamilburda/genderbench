## Dataset Attribution
This dataset was created by Scherer & Wallbott and is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License. 

- Original Source: [unige.ch](https://www.unige.ch/cisa/research/materials-and-online-research/research-material/)
- License: [https://creativecommons.org/licenses/by-nc-sa/3.0/](https://creativecommons.org/licenses/by-nc-sa/3.0/)
- Changes Made: Only event descriptions are extracted and filtered according to the following script

```python
samples = set()

for x in pd.read_csv("isear.csv").SIT:  # The CSV file was converted from the original MDB

    line = x.replace(" á\n", " ").replace("  ", " ").strip()  # Fixing newlines

    if "[" in line:  # Answers such as "[ No response ]"
        continue

    if len(line) >= 20:  # Answers such as "Nothing", "Does not apply", etc
        samples.add(line)

with open("isear_samples.txt", "w") as f:
    f.write("\n".join(samples))
```
