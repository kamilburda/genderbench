from setuptools import find_namespace_packages, setup


def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="genderbench",
    version="0.5.0",
    install_requires=read_requirements("requirements.txt"),
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    include_package_data=True,
    description="Evaluation suite for gender biases in LLMs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Matúš Pikuliak",
    author_email="matus.pikuliak@gmail.com",
    url="https://github.com/matus-pikuliak/genderbench",
    license="See README",
    project_urls={
        "Documentation": "https://genderbench.readthedocs.io/latest/",
        "Source Code": "https://github.com/matus-pikuliak/genderbench",
    },
    keywords="gender-bias fairness-ai llms llms-benchmarking",
)
