all: env

run: env
	env/bin/engine

tags:
	ctags -R .

env:
	python3 -m venv env
	env/bin/pip install wheel
	env/bin/pip install -e .
