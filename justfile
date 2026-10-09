set shell := ["bash", "-cu"]
set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
python := if os() == "windows" { "./.venv/Scripts/python.exe" } else { "./.venv/bin/python" }

default:
    @just --list

install:
    python -m venv .venv
    {{python}} -m pip install -r requirements-dev.txt

generate:
    {{python}} .github/scripts/update_resume.py

test:
    {{python}} -m unittest discover tests/

pdf:
    tectonic main.tex
    tectonic pt-br/main.tex

check: generate test

verify: check pdf
    {{python}} .github/scripts/verify_resume_pdf.py --source resume.yaml --pdf en=main.pdf --pdf pt-BR=pt-br/main.pdf --published en=resume.pdf --published pt-BR=pt-br/resume.pdf

preview port="4173":
    {{python}} -m http.server {{port}} --bind 127.0.0.1
