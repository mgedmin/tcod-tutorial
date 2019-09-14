.PHONY: all
all: env

.PHONY: run
run: env
	env/bin/engine

.PHONY: tags
tags:
	ctags -R .

env:
	python3 -m venv env
	env/bin/pip install wheel
	env/bin/pip install -e .
