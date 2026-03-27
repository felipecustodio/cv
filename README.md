<p align="center">
  <img src="assets/banner.png" />
</p>

<p align="center">
    Powered by <a href="https://github.com/wtfjoke/setup-tectonic">wtfjoke/setup-tectonic</a>
</p>

# YAML-Driven Resume/CV Generator

A modern, automated system for maintaining both web and PDF versions of your professional resume from a single YAML source.

## Project Overview

This project uses a single YAML data source to generate both a professional LaTeX PDF resume and an HTML website version. The LaTeX is compiled and rendered automatically via the setup-tectonic GitHub action, and deployed to the web via Vercel, hosted at [cv.felipecustodio.dev](https://cv.felipecustodio.dev).

The system also supports Overleaf git sync, allowing use of the Overleaf editor while syncing changes to the git repository.

## Features

- **Single Source of Truth**: Manage your resume data in one YAML file
- **Dual Output Formats**:
  - Professional PDF resume (LaTeX)
  - Modern HTML website
- **Automated Workflow**:
  - Update resume by simply editing the YAML file
  - Tests automatically run to validate changes
  - PDF and HTML outputs generated automatically
  - CI/CD pipeline for deployment
- **Extensible Design**: Easily customize HTML and LaTeX templates

## Project Structure

```
├── index.html          # HTML template/output
├── main.tex            # LaTeX template/output
├── resume.yaml         # Source data (edit this file!)
├── resume.pdf          # Generated PDF output
├── assets/             # Static assets for website
└── tests/              # Testing suite
    ├── test_update_resume.py
    ├── test_integration.py
    └── test_regex_patterns.py
```

## Getting Started

### Prerequisites

- Python 3.6+
- LaTeX environment (for local PDF generation)
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cv.git
   cd cv
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Usage

### Update Your Resume

1. Edit the `resume.yaml` file with updated information
2. Run the update script:
   ```bash
   python .github/scripts/update_resume.py
   ```
3. Your updates will be reflected in both `index.html` and `main.tex`

### Generate PDF Locally

To generate the PDF locally:

```bash
tectonic main.tex
```

## GitHub Actions Workflow

This project uses two main GitHub Actions workflows:

1. **Validate Resume Generation**:
   - Triggered on pull requests that affect resume sources, templates, generator, or tests
   - Runs tests and regeneration checks
   - Fails if generated `index.html` and `main.tex` are out of sync with committed files

2. **Update Resume from YAML**:
   - Triggered when `resume.yaml` is changed
   - Runs tests to validate changes
   - Updates HTML and LaTeX files
   - Commits changes back to the repository

3. **Build PDF Resume**:
   - Builds after the update workflow completes successfully
   - Compiles LaTeX to PDF
   - Makes PDF available as an artifact

## Testing

Run all tests:

```bash
python -m unittest discover tests/
```

## Deployment

The website is automatically deployed to Vercel when changes are pushed to the main branch.

## Customization

### Customize HTML Template

Edit the `index.html` file, maintaining the comment markers that serve as placeholders for dynamically generated content.

### Customize LaTeX Template

Edit the `main.tex` file, maintaining the section markers that serve as placeholders for dynamically generated content.

## Acknowledgments

- [wtfjoke/setup-tectonic](https://github.com/wtfjoke/setup-tectonic) for LaTeX compilation
- Vercel for website hosting
