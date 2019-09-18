.PHONY: all
all: env

.PHONY: run
run: env
	env/bin/engine

.PHONY: mypy
mypy: env
	env/bin/mypy --disallow-untyped-defs engine.py

.PHONY: tags
tags:
	ctags -R .

env:
	python3 -m venv env
	env/bin/pip install wheel
	env/bin/pip install -e .
