NAME     = a_maze_ing.py
PYTHON   = python3


all: run

install:
	$(PYTHON) -m pip install --user flake8 mypy

run:
	$(PYTHON) $(NAME)

debug:
	$(PYTHON) -m pdb $(NAME)

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
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -rf {} \;

.PHONY: all install run debug lint clean lint-strict
