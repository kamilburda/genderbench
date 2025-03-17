import pandas as pd
from nltk.tokenize import word_tokenize

diversity_med_qa = pd.read_csv("diversity_med_qa/GenderDataset.csv")

medqa = pd.concat(
    [
        pd.read_json("medqa/dev.jsonl", lines=True),
        pd.read_json("medqa/train.jsonl", lines=True),
        pd.read_json("medqa/test.jsonl", lines=True),
    ]
)

samples = list()

for row in diversity_med_qa.itertuples():

    tokens = word_tokenize(row.Question)
    tokens = [token.lower() for token in tokens]
    male_tokens = sum(
        tokens.count(t) for t in ["he", "man", "his", "him", "male", "boy", "men"]
    )
    female_tokens = sum(
        tokens.count(t) for t in ["she", "woman", "her", "female", "girl", "women"]
    )

    if male_tokens == female_tokens:
        continue

    if male_tokens == 0 or female_tokens == 0 or abs(male_tokens - female_tokens) > 2:
        if male_tokens > female_tokens:
            samples.append([row.Question, row._4])
        else:
            samples.append([row._4, row.Question])

for sample in samples:
    for medqa_row in medqa.itertuples():
        if medqa_row.question in sample:
            sample.append(list(medqa_row.options.values()))
            sample.append(ord(medqa_row.answer_idx) - ord("A"))

df = pd.DataFrame(
    samples, columns=["male_sentence", "female_sentence", "options", "correct_option"]
)
df.to_csv("diversity_med_qa_extracted.csv", index=False)
