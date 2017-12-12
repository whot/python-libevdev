all: doc test

doc:
	sphinx-apidoc -f -o doc/source libevdev
	sphinx-build -b html doc/source doc/html

test:
	PYTHONPATH=. python3 -m unittest test

.PHONY: doc test
