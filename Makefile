all: doc test

doc:
	sphinx-apidoc -f -o doc/source libevdev
	sphinx-build -b html doc/source doc/html

test:
	PYTHONPATH=. pytest-3 test/*.py

.PHONY: doc test
