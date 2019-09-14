all: env

run: env
	env/bin/engine

env:
	python3 -m venv env
	env/bin/pip install wheel
	env/bin/pip install -e .
