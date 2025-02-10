.PHONY: install test lint docs clean build publish

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=inferra

lint:
	flake8 inferra tests
	black --check inferra tests
	mypy inferra tests

docs:
	cd docs && make html

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} +

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*
