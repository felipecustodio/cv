<p align="center">
  <img src="assets/banner.png" />
</p>

<p align="center">
    Powered by <a href="https://github.com/wtfjoke/setup-tectonic">wtfjoke/setup-tectonic</a>
</p>

# YAML-Driven Resume/CV Generator

A modern, automated system for maintaining both web and PDF versions of your professional resume from a single YAML source.

## Project Overview

This project uses a single YAML data source to generate localized LaTeX PDF resumes and HTML website versions. English is served at the root, while Brazilian Portuguese is served at `/pt-br/`. The LaTeX is compiled and rendered automatically via the setup-tectonic GitHub action, and deployed to the web via Vercel, hosted at [cv.felipecustodio.dev](https://cv.felipecustodio.dev).

The system also supports Overleaf git sync, allowing use of the Overleaf editor while syncing changes to the git repository.

## Features

- **Single Source of Truth**: Manage your resume data in one YAML file
- **Dual Output Formats**:
  - Professional PDF resume (LaTeX)
  - Modern HTML website
- **Localized Versions**: English and Brazilian Portuguese content, interface strings, dates, PDFs, and web pages are generated from `resume.yaml`
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
├── pt-br/              # Brazilian Portuguese generated HTML, LaTeX, and PDF
├── assets/             # Static assets for website
└── tests/              # Testing suite
    ├── test_update_resume.py
    ├── test_integration.py
    ├── test_regex_patterns.py
    └── test_verify_resume_pdf.py
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Tectonic and just
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cv.git
   cd cv
   ```

2. Create the virtual environment and install the dependencies:
   ```bash
   just install
   ```

## Usage

### Update the resume

1. Edit `resume.yaml`.
2. Run `just generate` to update both HTML files and both LaTeX files.

### Generate and verify the PDFs

Run `just verify`. This command generates the source files, runs the tests, and compiles both PDFs.
It also checks that each PDF has one page and that its extractable text contains the localized YAML content.
The PDF compiler writes `main.pdf` and `pt-br/main.pdf`. The release workflow publishes them as `resume.pdf` in each locale.

This check is not an ATS scan. It does not upload the resume or predict how a hiring system parses it.

## GitHub Actions Workflow

This project uses two main GitHub Actions workflows:

1. **Validate Resume Generation**:
   - Runs `just verify` for pull requests that change the resume or its build files
   - Fails if either PDF has more than one page or omits extractable YAML content
   - Fails if generated HTML or LaTeX differs from the committed files

2. **Update Resume from YAML**:
   - Triggered when `resume.yaml` is changed
   - Runs tests to validate changes
   - Updates HTML and LaTeX files for every locale configured in `resume.yaml`
   - Commits changes back to the repository

3. **Build PDF Resume**:
   - Builds after the update workflow completes successfully
   - Compiles every localized LaTeX source to its matching PDF
   - Commits the generated PDFs and makes them available as artifacts

## Testing

Run `just test` for the unit tests. Run `just verify` for the complete generation and PDF check.

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
