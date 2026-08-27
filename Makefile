PYTHON = python3

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) -m src.main maps/easy/02_simple_fork.txt

debug:
	$(PYTHON) -m pdb -m src.main maps/easy/02_simple_fork.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
