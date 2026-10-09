import subprocess
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf
import yaml


SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "verify_resume_pdf.py"


class VerifyResumePdfTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.source = Path(self.temp_dir.name) / "resume.yaml"
        self.pdf = Path(self.temp_dir.name) / "resume.pdf"
        self.published = Path(self.temp_dir.name) / "published.pdf"
        self.source.write_text(yaml.safe_dump({
            "site": {"locales": {"en": {"directory": "."}}},
            "basics": {
                "name": "Example Engineer",
                "label": {"en": "Software Engineer"},
                "email": "example@example.org",
                "profiles": [{"network": "GitHub", "username": "example"}],
            },
            "work": [{
                "name": "Example Company",
                "position": {"en": "Backend Engineer"},
                "location": {"en": "Remote"},
                "startDate": "2022-01-01",
                "endDate": "2024-02-01",
                "summary": {"en": "Built a service for billing."},
                "highlights": {"en": ["Reduced failed billing jobs."]},
            }],
            "education": [{
                "institution": {"en": "Example University"},
                "location": {"en": "Example City"},
                "degree": {"en": "Bachelor of Science"},
                "endDate": "2021-12-01",
                "courses": {"en": ["Distributed systems"]},
            }],
            "skills": [
                {"name": {"en": "Languages"}, "keywords": {"en": ["English (Native)"]}},
                {"name": {"en": "Skills and Tools"}, "keywords": {"en": ["Python", "SQL"]}},
            ],
        }), encoding="utf-8")

    def write_pdf(self, *, include_result=True, include_education_location=True,
                  pages=1, published_font_size=None):
        text = [
            "Example Engineer", "Software Engineer", "example@example.org", "example",
            "Example Company", "Backend Engineer", "Remote", "Jan. 2022", "Feb. 2024",
            "Built a service for billing.",
        ]
        if include_result:
            text.append("Reduced failed billing jobs.")
        text.extend(["Example University", "Bachelor of Science", "Dec. 2021"])
        if include_education_location:
            text.append("Example City")
        text.extend([
            "Distributed systems", "Languages", "English (Native)",
            "Skills and Tools", "Python", "SQL",
        ])
        document = pymupdf.open()
        document.new_page().insert_text((40, 50), "\n".join(text), fontsize=11)
        for _ in range(pages - 1):
            document.new_page()
        document.save(self.pdf)
        document.close()
        if published_font_size is None:
            shutil.copyfile(self.pdf, self.published)
        else:
            published = pymupdf.open()
            published.new_page().insert_text((40, 50), "\n".join(text),
                                             fontsize=published_font_size)
            published.save(self.published)
            published.close()

    def verify(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--source", str(self.source),
             "--pdf", f"en={self.pdf}", "--published", f"en={self.published}"],
            capture_output=True, text=True, check=False,
        )

    def test_one_page_with_all_source_facts_passes(self):
        self.write_pdf()
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_achievement_fails(self):
        self.write_pdf(include_result=False)
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Reduced failed billing jobs.", result.stderr)

    def test_second_page_fails(self):
        self.write_pdf(pages=2)
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("one page", result.stderr)

    def test_missing_education_location_fails(self):
        self.write_pdf(include_education_location=False)
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Example City", result.stderr)

    def test_stale_published_text_fails(self):
        self.write_pdf()
        with pymupdf.open(self.published) as document:
            document[0].insert_text((40, 500), "Obsolete achievement")
            stale = Path(self.temp_dir.name) / "stale.pdf"
            document.save(stale)
        self.published = stale
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("differs", result.stderr)

    def test_stale_published_layout_fails(self):
        self.write_pdf(published_font_size=9)
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("differs", result.stderr)


if __name__ == "__main__":
    unittest.main()
