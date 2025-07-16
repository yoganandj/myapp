# Makefile for data_delivery

.PHONY: all clean install test

all: install

install:
	pip install -e .

test:
	tox

clean:
	rm -rf *.egg-info .tox
