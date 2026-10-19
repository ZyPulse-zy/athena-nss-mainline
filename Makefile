PYTHON ?= python3

.PHONY: check catalog test

check:
	$(PYTHON) tools/catalog.py check
	$(PYTHON) tools/check_repository.py

catalog:
	$(PYTHON) tools/catalog.py build

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_catalog.py' -v
