## Dataset Attribution

Some of the values in this dataset were extracted from [Kennison & Trofe 2003](https://link.springer.com/content/pdf/10.1023/A:1023599719948.pdf).
The reported scores from the paper were filtered to only include occupations
and we only store average score in the dataset. We also include the frequency
of each noun as reported by Google Ngram.

The use of the aggregated data from the paper is believed to be *fair use* for
the reasons stated in the `FAIR_USE.md` file.

## Columns

### `noun`

The noun that is being rated. Most of these are _occupations_, but there are
some exceptions, e.g. _killer_, _father_.

### `score`

The stereotypical score assigned to the `noun` annotators. This is the average
of scores reported by men and women from the paper. The instructions for
annotators were as follows:

```
The following list contains everyday nouns. We would like you to consider how
likely you feel that the noun represents a person who is male or a person who is
female. A rating of “1” would indicate that a particular noun is very likely to
represent a person who is female. A rating of “7” would indicate that a
particular noun is very likely to represent a person who is male. A rating of
“4” would indicate that a particular noun is equally likely to represent a
person who is male or female. A rating of “2” or “3” and “5” and “6” would
indicate different degrees of likelihood that a particular noun represents a
person who is female or male. Circle only one rating for each item. Some nouns
may seem easier to rate than others. Be sure to circle the rating that reflects
your own opinion.
```

### `frequency`

Log-frequency of the `noun` in the last 20 years according to Google Ngram.

```python
import math
import requests

import numpy as np

def frequency(noun):
    url = f'https://books.google.com/ngrams/json?content={noun}&year_start=2000&year_end=2020&corpus=26&smoothing=3'
    r = requests.get(url).json()[0]
    return math.log(np.mean(r['timeseries']) + 1e-12, 10)
```