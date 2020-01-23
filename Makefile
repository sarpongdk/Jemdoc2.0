VENV=env

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean         to remove build files"
	@echo "  clean-pyc     to remove .pyc files"
	@echo "  build         to build the project for distribution"
	@echo "  install       to install the project locally"
	@echo "  create-env    to initialize project in a virtual environment in the current working directory"
	@echo "  init    to download project dependencies from requirements.txt"

clean-pyc:
	find . -name "*.pyc" -exec rm {} +

clean:
	rm -r dist/
	rm -r build/
	rm -r jemdoc.egg-info/
	rm -r $(VENV)   

build:
	python2 setup.py bdist_wheel sdist

install:
	python2 setup.py install

create-env:
	virtualenv -p /usr/bin/python2.7 $(VENV)

init:
	pip install -r requirements.txt
