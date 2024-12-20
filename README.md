# GenderBench - Evaluation suite for gender biases in LLMs


`GenderBench` is an evaluation suite that comprehensively benchmarks gender biases
in large language models (LLMs). `GenderBench` aims to identify unfair behavior
with respect to the gender of the user or the gender of people mentioned
in the processed texts. `GenderBench` consists of many `Probes`, each focused on
different use case, domain, bias, and so on. `GenderBench` mostly aggregates
existing methodologies, but it also contains original and novel ideas.

## Installation

You can install the package from this repository:

```
pip install git+https://github.com/matus-pikuliak/gender_bench
```

## Usage

`GenderBench` can be used to evaluate an arbitrary text generator, i.e., anything
that is able to call `generate(input: str) -> str` method.

### Probes
The basic use case is to evaluate a `generator` with a single probe:

```python
# GestCreative asks model to write a character profile based on a stereotypical
# prompt. Then it analyzes the genders of the generated characters.
from gender_bench.generators.random_generator import RandomGenerator
from gender_bench.probes.creative.gest_creative.gest_creative_probe import GestCreativeProbe


generator = RandomGenerator(["He was a punk", "She did ballet"])
probe = GestCreative(template=GestCreativeProbe.templates[0], num_repetitions=10)
probe.run(generator)

>> {
>>      "masculine_rate": 0.5007705894713239,
>>      "stereotype_rate": -0.002398816752873345,
>>      ...
>> }
```

Each probe returns a set of appropriate scores that need to be interpreted. In
this case, the main score is `stereotype_rate` which is close to zero, as we are
randomly generated either a male-coded or a female-coded text.

### Harnesses

To run a comprehensive evaluation, probes are organized into predefined sets
called `harnesses`. A harness returns only the pre-defined metrics that are
deemed important for an experiment. Currently, there is only one harness in the
repository, the `DefaultHarness`:

```python
from gender_bench.harnesses.default import DefaultHarness

harness = DefaultHarness(calculate_cis=True)
harness.run(generator)

>>> {
>>>     'GestCreativeProbe': {'stereotype_rate': 0.00224880192056498},
>>>     'InventoriesProbe': {'correlation': 0.012060006315442866},
>>>     ...
>>> }
```

## Probes

### Affective computing

These probes study how the models handle tasks related to affective computing,
i.e., working with the emotional state of the user and emotionality in the text.

- `Dreaddit` - We ask the model to predict how stressed the author of a text is. 
We study whether the model exhibits different perceptions of stress based on the 
gender of the author. [Documentation](./src/gender_bench/probes/affective/dreaddit/README.md).

- `Isear` - We ask the model to role-play as a person of a specific gender and 
inquire about its emotional response to various events. We study whether the 
model exhibits different perceptions of emotionality based on gender. 
[Documentation](./src/gender_bench/probes/affective/isear/README.md).

### Creative writing

These probes study how the models use stereotypes when they are
prompted to do creative writing.

- `GestCreative` -We ask the model to generate a character profile for a novel 
based on a motto. The mottos are associated with various gender stereotypes. We 
study what gender does the model use for the character. [Documentation](./src/gender_bench/probes/creative/gest_creative/README.md).

- `Inventories` - We ask the model to generate a character profile based on a 
simple description. The descriptions come from gender inventories and are 
associated with various gender stereotypes. We study what gender does the model 
use for the character. [Documentation](./src/gender_bench/probes/creative/inventories/README.md).

- `JobsLum` - We ask the model to generate a character profile based on an 
occupation. We compare the gender of the generated characters with the 
stereotypically gender associated with the occupations. [Documentation](./src/gender_bench/probes/creative/jobs_lum/README.md).

### Decision making

These probes study whether the models discriminate against certain genders
when they are prompted to make a decision about typical life situations.

- `DiscriminationTamkin` - The model is asked to make a yes-or-no decision about 
various questions (e.g., should a person get a loan, should a person get a job 
offer). The gender of the person is specified. We study whether the model gives 
better outcomes to any genders. [Documentation](./src/gender_bench/probes/decision_making/discrimination_tamkin/README.md).

- `HiringAn` - The model is asked about a candidate for a job. The candidate is 
described using a gender-coded name. We study how the candidate's name 
correlates with the stereotypical gender associated with the job. [Documentation](./src/gender_bench/probes/decision_making/hiring_an/README.md).

- `HiringBloomberg` - The model is asked to select rank candidates from a list 
of CVs. The CVs contain gender-coded name. We study which genders tend to win 
for different occupations. [Documentation](./src/gender_bench/probes/decision_making/hiring_bloomberg/README.md).

### Assessing opinions

These probes study what the opinions of the models are when asked.

- `BBQ` - The BBQ dataset contains trick multiple-choice questions that test 
whether the model uses gender-stereotypical reasoning. [Documentation](./src/gender_bench/probes/opinion/bbq/README.md).

- `Direct` - We ask the model whether it agrees with various steretypical 
statements about genders.
 [Documentation](./src/gender_bench/probes/opinion/direct/README.md).

- `Gest` - We ask the model questions that can be answered using either logical 
or stereotypical reasoning. We observe how often stereotypical reasoning is 
used. [Documentation](./src/gender_bench/probes/opinion/gest/README.md).


## Design philosophy

- We want to cover as many possibilities of using LLMs as possible.
- Data and methodological _quality_ are of utmost importance. Each data source
is manually evaluated and judged.
- Each probe measures a behavior that can be considered _harmful_ in one way
or another.
- The analysis of the results should be _trustworthy_. Analyzing texts with ML
models is not done until proven reliable enough.
- If possible, non-binary genders should be included.

## Probe design

### Probe anatomy

```                                                                
 ┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌───────────┐ 
 │  Probe  ├─────┤  ProbeItem  ├─────│  Prompt  │─────│  Attempt  │ 
 └─────────┘    *└─────────────┘    *└──────────┘    *└───────────┘ 
```

- Each `Probe` is designed to measure a single well defined behavior of the
evaluated `generator`, e.g., _how does a generator order gender-coded CVs_. The
result of running a probe is a _metric_.
- Each `Probe` measures the behavior by running many `Prompts`. `Prompts` are
specific text inputs that are being fed into the evaluated `generator`.
- Logically related `Prompts` are grouped in `ProbeItems`, e.g., if we have a
multiple-choice question, we might wish to reorder the choices to tackle order
bias that might be present in a model. A single `ProbeItem` would then contain
all the possible reorderings as `Prompts`.
- After we run the generation process, each `Prompt` is populated with one or
more `Attempts`. `Attempts` are the generations being generated by the
`generator` for given `Prompts`.

### Probe lifecycle

Running a probe consists of four phases, as seen in the `Probe.run` method:

1. **Prompt Creation**. The probe is populated with `ProbeItems` and `Prompts`.
All the texts that will be fed into the generator are prepared at this stage,
along with appropriate metadata.
2. **Attempt Generation**. The generator is used to process the `Prompts` and
the generate texts are stored in `Attempts`.
3. **Attempt Evaluation**. The generated texts in `Attempts` are evaluated with
appropriate evaluators. The evaluation is an assessment of the evaluated text,
e.g., was a correct letter selected for a multiple-choice question?
4. **Metric Calculation**. The evaluations in `Attempts` are aggregated to
calculate a final set of metrics for the `Probe`.
