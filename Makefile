all: doc

doc:
	sphinx-apidoc -f -o doc/source libevdev
	sphinx-build -b html doc/source doc/html

.PHONY: doc
