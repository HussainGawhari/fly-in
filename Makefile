PYTHON = python3

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	@test -n "$(FILE)" || (echo "Usage: make run FILE=<map_file>"; exit 1)
	$(PYTHON) -m src.main "$(FILE)"

debug:
	@test -n "$(FILE)" || (echo "Usage: make debug FILE=<map_file>"; exit 1)
	$(PYTHON) -m pdb -m src.main "$(FILE)"

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
