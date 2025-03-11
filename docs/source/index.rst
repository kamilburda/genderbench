.. GenderBench documentation master file, created by
   sphinx-quickstart on Thu Jan 16 20:18:05 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GenderBench Documentation
=========================

This is the documentation for `GenderBench <https://github.com/matus-pikuliak/gender_bench>`_
project. `GenderBench` is an evaluation suite designed to measure and benchmark
gender biases in large language models. It uses a variety of tests, called
**probes**, each targeting a specific type of unfair behavior. Our goal is to
cover as many types of unfair behavior as possible.

This project has two purposes:

1. **To publish the results we measured for various LLMs.** Our goal is to
inform the public about the state of the field and raise awareness about the
gender-related issues that LLMs have.

2. **To allow researchers to run the benchmark on their own LLMs.** Our goal is
to make the research in the area easier and more reproducible. `GenderBench` can
serve as a base to pursue various fairness-related research questions.

.. toctree::
   :caption: Table of Contents
   :maxdepth: 2
   
   quickstart
   developing_probes
   reports
   probes
   api

