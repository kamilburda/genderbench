.. _probe_cards:

Probe Cards
===========

Each `Probe` is documented with its own ``README`` file. This document describes
the schema used to create these files. We describe the documents field by field
as they are written.

- Abstract
    Abstract succintly describes the main idea behind the probe.
- Harms
    Description of harms measured by the probe.
- Use case
    What is the use case for using LLMs in the context of the prompt.
- Genders
    What genders are considered.
- Genders definition
    How is the gender indicated in the texts (explicitly stated, gender-coded
    pronouns, gender-coded names, etc).
- Genders placement
    Whose gender is being processed, e.g., author of a text, user, subject of
    a text.
- Language
    Natural language used in the prompts / responses.
- Output type
    What is type of the output, e.g., structured responses, free text.
- Modality
    What is the modality of the conversation, e.g., single turn text
    chats, tools, image generation.
- Domain
    What is domain of the data used, e.g., everyday life, healthcare, business.
- Realistic format
    Is the format of prompts realistic? Is it possible that similar requests
    could be used by common users? Do the queries make practical sense outside
    of the probing context?
- Data source
    How were the data created, e.g., human annotators, LLMs, scraping.
- Size
    Number of probe items.
- Intersectionality
    Are there non-gender-related harms that could be addressed by the probe,
    e.g., race, occupation.
- Folder
    Where is the code located.
- Methodology
    - Probe Items
        Description of how are the probe items created.
    - Data
        Description of the necessary data used to create the probe items.
    - Evaluation
        Description of the answer evaluation methodology.
    - Metrics
        Description of all the calculated metrics.
- Sources
    List of all the resources that can improve the understanding of the probe,
    e.g., related papers or datasets.
- Probe parameters
    Documentation for the parameters used when the probe is initialized in the
    code.
- Limitations / Improvements
    Discussion about the limitations of the probe and ideas about how to improve
    it in the future.
