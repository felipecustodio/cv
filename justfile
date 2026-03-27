set shell := ["zsh", "-cu"]

default:
    @just --list

install:
    .venv/bin/python -m pip install -r requirements-dev.txt

generate:
    .venv/bin/python .github/scripts/update_resume.py

test:
    .venv/bin/python -m unittest discover tests/

pdf:
    tectonic main.tex

check: generate test

preview port="4173":
    .venv/bin/python -m http.server {{port}} --bind 127.0.0.1
