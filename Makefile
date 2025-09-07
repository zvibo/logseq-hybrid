.PHONY: install test check

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip -r requirements.txt -e .

check:
	. .venv/bin/activate && python -m logseq_hybrid.cli check

test:
	. .venv/bin/activate && pytest -q
