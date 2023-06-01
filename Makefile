lint:
	@echo
	ruff .
	@echo
	black --check --diff --color .
	@echo
	pip-audit

format:
	ruff --silent --exit-zero --fix .
	black .

precommit:
	make lint
	make format

venv:
	python3 -m venv ecout_env

install:
	pip install -r requirements.txt