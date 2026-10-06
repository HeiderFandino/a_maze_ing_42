NAME   = a_maze_ing.py
PYTHON = python3
CONFIG = config.txt

all: run

install:
	$(PYTHON) -m pip install flake8 mypy

run:
	$(PYTHON) $(NAME) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(NAME) $(CONFIG)

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) \
		-prune -exec rm -rf {} \;

.PHONY: all install run debug lint lint-strict clean
