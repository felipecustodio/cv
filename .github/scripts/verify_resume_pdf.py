#!/usr/bin/env python3
"""Check PDF text and page count against the localized YAML resume."""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

from update_resume import (
    build_degree_text,
    format_date,
    get_locales,
    load_yaml_data,
    localize_resume_data,
)


def normalize(text):
    text = unicodedata.normalize("NFC", str(text)).replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip()


def expected_fields(data, locale):
    localized = localize_resume_data(data, locale)
    basics = localized.get("basics", {})
    for field in ("name", "label", "email"):
        yield basics.get(field, "")
    for profile in basics.get("profiles", []):
        yield profile.get("username", "")

    for job in localized.get("work", []):
        for field in ("name", "position", "location", "summary"):
            yield job.get(field, "")
        yield format_date(job.get("startDate"), locale)
        yield format_date(job.get("endDate"), locale)
        yield from job.get("highlights", [])

    for education in localized.get("education", []):
        yield education.get("institution", "")
        yield build_degree_text(education)
        if education.get("startDate"):
            yield format_date(education["startDate"], locale)
        if education.get("endDate"):
            yield format_date(education["endDate"], locale)
        yield from education.get("courses", [])

    for skill in localized.get("skills", []):
        yield skill.get("name", "")
        yield from skill.get("keywords", [])


def verify_pdf(path, data, locale):
    with pymupdf.open(path) as document:
        if len(document) != 1:
            return [f"expected one page, found {len(document)}"]
        extracted = normalize(document[0].get_text())

    return [f"missing PDF text: {field}" for field in expected_fields(data, locale)
            if field and normalize(field) not in extracted]


def main():
    parser = argparse.ArgumentParser(description="Check generated PDF pages and extractable YAML content")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--pdf", action="append", required=True, metavar="LOCALE=PATH")
    args = parser.parse_args()

    data = load_yaml_data(args.source)
    locales = get_locales(data)
    paths = {}
    for item in args.pdf:
        locale, separator, path = item.partition("=")
        if not separator or locale in paths:
            parser.error(f"invalid or duplicate PDF argument: {item}")
        paths[locale] = Path(path)
    if set(paths) != set(locales):
        parser.error(f"expected PDF locales {', '.join(locales)}; got {', '.join(paths)}")

    failures = []
    for locale, path in paths.items():
        try:
            errors = verify_pdf(path, data, locale)
        except (OSError, pymupdf.FileDataError) as error:
            errors = [str(error)]
        failures.extend(f"{locale} ({path}): {error}" for error in errors)
        if not errors:
            print(f"{locale} ({path}): one page; YAML content is extractable")
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
