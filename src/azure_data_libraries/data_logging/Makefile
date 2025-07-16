PIP_CACHE ="/tmp/pipcache"

setup-build:
	pip3 install --q "tox>4"

install:
	pip3 install -U setuptools
	pip3 install -e .
	pip3 install -e .[test]

check: setup-build
	tox -e lint

lint: setup-build
	tox -e lint

lint-quick-fix:
	tox -e lint-quick-fix
