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
        yield education.get("location", "")
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
            return [f"expected one page, found {len(document)}"], None
        page = document[0]
        extracted = normalize(page.get_text())
        spans = tuple(
            (span["font"], round(span["size"], 1),
             tuple(round(coordinate, 1) for coordinate in span["bbox"]))
            for block in page.get_text("dict")["blocks"] if "lines" in block
            for line in block["lines"] for span in line["spans"]
        )

    errors = [f"missing PDF text: {field}" for field in expected_fields(data, locale)
              if field and normalize(field) not in extracted]
    return errors, (extracted, spans)


def main():
    parser = argparse.ArgumentParser(description="Check PDF pages, YAML content, and published copies")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--pdf", action="append", required=True, metavar="LOCALE=PATH")
    parser.add_argument("--published", action="append", required=True, metavar="LOCALE=PATH")
    args = parser.parse_args()

    data = load_yaml_data(args.source)
    locales = get_locales(data)
    paths_by_kind = {}
    for kind, items in (("compiled", args.pdf), ("published", args.published)):
        paths = {}
        for item in items:
            locale, separator, path = item.partition("=")
            if not separator or locale in paths:
                parser.error(f"invalid or duplicate {kind} PDF argument: {item}")
            paths[locale] = Path(path)
        if set(paths) != set(locales):
            parser.error(f"expected {kind} PDF locales {', '.join(locales)}; got {', '.join(paths)}")
        paths_by_kind[kind] = paths

    failures = []
    signatures = {}
    for kind, paths in paths_by_kind.items():
        for locale, path in paths.items():
            try:
                errors, signature = verify_pdf(path, data, locale)
            except (OSError, pymupdf.FileDataError) as error:
                errors, signature = [str(error)], None
            signatures[kind, locale] = signature
            failures.extend(f"{locale} ({path}): {error}" for error in errors)
            if not errors:
                print(f"{locale} ({path}): one page; YAML content is extractable")
    for locale in locales:
        compiled = signatures["compiled", locale]
        published = signatures["published", locale]
        if compiled is not None and published is not None and compiled != published:
            failures.append(f"{locale}: published PDF differs from compiled PDF")
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
