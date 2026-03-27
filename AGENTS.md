# Repository Guidelines

## Project Structure & Module Organization
This repository is a YAML-driven resume generator. Edit `resume.yaml` as the single source of truth, then regenerate outputs:
- `index.html`: web resume template/output
- `main.tex`: LaTeX resume template/output
- `resume.pdf`: generated PDF artifact
- `assets/`: static files (for example, `assets/banner.png`)
- `tests/`: Python `unittest` suite (`test_update_resume.py`, `test_integration.py`, `test_regex_patterns.py`)
- `.github/scripts/update_resume.py`: generation logic used locally and in CI
- `.github/workflows/`: automation for update/build pipelines

## Build, Test, and Development Commands
Run from repository root.

```bash
pip install -r requirements-dev.txt
```
Installs Python dependencies used by local generation and tests.

```bash
python .github/scripts/update_resume.py
```
Regenerates `index.html` and `main.tex` from `resume.yaml`.

```bash
python -m unittest discover tests/
```
Runs all tests validating parsing, replacement logic, and integration flow.

```bash
tectonic main.tex
```
Builds `resume.pdf` locally from LaTeX.

## Coding Style & Naming Conventions
Use Python 3 with 4-space indentation and standard-library-first imports. Keep script functions focused and side-effect boundaries explicit (load data, transform, write output). Prefer descriptive snake_case for Python identifiers (`load_yaml_data`, `update_html_file`). Keep YAML keys consistent with existing schema (`basics`, `work`, `education`, `skills`) to avoid template/test breakage.

No dedicated formatter/linter is configured in-repo; match surrounding style and keep diffs minimal.

## Testing Guidelines
Testing uses `unittest`. Add or update tests in `tests/` whenever changing `.github/scripts/update_resume.py`, section markers, or regex replacements.
- Name files `test_*.py` and test methods `test_*`.
- Prefer fixture-driven tests with temporary files for end-to-end update flows.
- Validate both content presence and replacement behavior (old content removed, new content inserted).
- Keep generated artifacts in sync: pull requests should pass `Validate Resume Generation`, which reruns the generator and checks for uncommitted diffs.

## Commit & Pull Request Guidelines
Recent history mixes Conventional Commit style and sentence-case summaries. Prefer concise, imperative messages like:
- `feat: support new resume section`
- `fix: correct education regex replacement`
- `test: add edge cases for nested HTML sections`

For PRs, include:
- clear summary of changed resume behavior
- linked issue (if applicable)
- notes on manual verification (`update_resume.py`, `unittest`, `tectonic`)
- before/after screenshots when HTML presentation changes
