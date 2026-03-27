# Workflow Hardening and Generation Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve CI reliability, prevent silent generation failures, and make resume rendering safer and more maintainable across all 8 identified fixes.

**Architecture:** Split CI responsibilities into validation vs. mutation, then harden the generator with explicit replacement guards and LaTeX escaping. Keep changes incremental and test-driven, with each task introducing one behavior change and corresponding test updates.

**Tech Stack:** GitHub Actions, Python 3 (`unittest`, `yaml`, `re`, `importlib`), Tectonic.

---

## File Map

- Create: `.github/workflows/validate-resume.yml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Modify: `.github/workflows/update-resume.yml`
- Modify: `.github/workflows/action.yml`
- Modify: `.github/scripts/update_resume.py`
- Modify: `tests/test_update_resume.py`
- Modify: `tests/test_integration.py`
- Modify: `tests/test_regex_patterns.py`
- Modify: `README.md`
- Modify: `AGENTS.md`

### Task 1: Split CI validation from mutation

**Files:**
- Create: `.github/workflows/validate-resume.yml`
- Modify: `.github/workflows/update-resume.yml`

- [ ] **Step 1: Write failing workflow test condition (local sanity check)**
Define expected triggers: validation on `pull_request`, mutation only on `push` to `main` with `resume.yaml` changes.

- [ ] **Step 2: Add validation workflow**
Create `.github/workflows/validate-resume.yml`:
- Trigger: `pull_request`, paths `resume.yaml`, `index.html`, `main.tex`, `.github/scripts/update_resume.py`, `tests/**`
- Steps: checkout, setup Python, install deps, run `python -m unittest discover tests/`, run generator, fail if dirty (`git diff --exit-code`).

- [ ] **Step 3: Restrict mutation workflow scope**
Keep `.github/workflows/update-resume.yml` for main-branch mutation only; add explicit `permissions: contents: write`, and leave commit step there.

- [ ] **Step 4: Verify syntax**
Run: `python -m unittest discover tests/`
Expected: PASS (workflow logic validated via file inspection + existing test suite).

### Task 2: Remove duplicate PDF builds

**Files:**
- Modify: `.github/workflows/action.yml`

- [ ] **Step 1: Remove duplicate trigger path**
Keep only `workflow_run` (plus optional `workflow_dispatch`), remove broad `push`.

- [ ] **Step 2: Tighten condition**
Guard execution to successful upstream run only.

- [ ] **Step 3: Verify behavior**
Document expected single build per YAML change in workflow comments.

### Task 3: Fail fast when template markers are missing

**Files:**
- Modify: `.github/scripts/update_resume.py`
- Modify: `tests/test_regex_patterns.py`
- Modify: `tests/test_update_resume.py`

- [ ] **Step 1: Write failing tests**
Add tests asserting generator raises `ValueError` when Experience/Education/Skills anchors are missing in HTML or LaTeX.

- [ ] **Step 2: Implement minimal replacement guards**
Use `re.subn` and assert replacement count is `1` for each section.

- [ ] **Step 3: Run focused tests**
Run: `python -m unittest tests.test_update_resume tests.test_regex_patterns`
Expected: PASS.

### Task 4: Escape LaTeX-special characters from YAML content

**Files:**
- Modify: `.github/scripts/update_resume.py`
- Modify: `tests/test_update_resume.py`

- [ ] **Step 1: Add failing unit tests**
Cover fields containing `_ % & # $ { } ~ ^ \` across header/work/education/skills.

- [ ] **Step 2: Implement `escape_latex()` helper**
Apply escaping consistently before injecting user text into LaTeX templates.

- [ ] **Step 3: Verify**
Run: `python -m unittest tests.test_update_resume`
Expected: PASS and escaped tokens present.

### Task 5: Remove unused dependency and pin install inputs

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Modify: `.github/workflows/update-resume.yml`
- Modify: `.github/workflows/validate-resume.yml`
- Modify: `README.md`

- [ ] **Step 1: Define dependency files**
`requirements.txt`: runtime deps only (`PyYAML`).
`requirements-dev.txt`: `-r requirements.txt` (+ optional test-only packages if needed).

- [ ] **Step 2: Update workflows**
Replace inline `pip install pyyaml jinja2` with `pip install -r requirements-dev.txt`.

- [ ] **Step 3: Update docs**
Replace manual dependency command in `README.md`.

### Task 6: Improve output correctness tests

**Files:**
- Modify: `tests/test_integration.py`
- Modify: `tests/test_update_resume.py`

- [ ] **Step 1: Add stronger assertions**
Assert each target section is replaced exactly once and stale placeholder text is removed.

- [ ] **Step 2: Add integration smoke check for generation stability**
After running generator, verify deterministic markers exist and no old fixture markers remain.

- [ ] **Step 3: Run suite**
Run: `python -m unittest discover tests/`
Expected: PASS.

### Task 7: Replace deprecated `imp` import path

**Files:**
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Add failing compatibility test**
Ensure module load works through `importlib` fallback path.

- [ ] **Step 2: Replace `imp.load_source`**
Use `importlib.util.spec_from_file_location` + `module_from_spec`.

- [ ] **Step 3: Verify**
Run: `python -m unittest tests.test_integration`
Expected: PASS with no deprecation usage.

### Task 8: Make degree rendering data-driven

**Files:**
- Modify: `.github/scripts/update_resume.py`
- Modify: `tests/test_update_resume.py`
- Modify: `README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add failing tests for diverse degree values**
Use YAML inputs like `Master`, `Bachelor`, `PhD`, custom `degree` field.

- [ ] **Step 2: Implement rendering precedence**
Use explicit YAML text (`degree` or `studyType` + `area`) without hardcoding MBA/BSc assumptions.

- [ ] **Step 3: Verify**
Run: `python -m unittest tests.test_update_resume`
Expected: PASS with accurate output in HTML and LaTeX.

## Final Verification and Delivery

- [ ] Run full test suite:
`python -m unittest discover tests/`
- [ ] Run generator:
`python .github/scripts/update_resume.py`
- [ ] Build PDF smoke test:
`tectonic main.tex`
- [ ] Confirm no unintended drift:
`git status --short`
- [ ] Prepare PR with grouped commits:
1. CI split + trigger cleanup
2. Generator safety (subn + escaping)
3. Test hardening + importlib
4. Dependency cleanup + docs

