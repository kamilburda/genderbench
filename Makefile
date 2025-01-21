format:
	isort . --profile black
	black .
	flake8 --ignore=E501,W503 .

test:
	pytest -s tests/test_probes.py