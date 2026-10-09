import subprocess
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
                "degree": {"en": "Bachelor of Science"},
                "endDate": "2021-12-01",
                "courses": {"en": ["Distributed systems"]},
            }],
            "skills": [
                {"name": {"en": "Languages"}, "keywords": {"en": ["English (Native)"]}},
                {"name": {"en": "Skills and Tools"}, "keywords": {"en": ["Python", "SQL"]}},
            ],
        }), encoding="utf-8")

    def write_pdf(self, *, include_result=True, pages=1):
        text = [
            "Example Engineer", "Software Engineer", "example@example.org", "example",
            "Example Company", "Backend Engineer", "Remote", "Jan. 2022", "Feb. 2024",
            "Built a service for billing.",
        ]
        if include_result:
            text.append("Reduced failed billing jobs.")
        text.extend([
            "Example University", "Bachelor of Science", "Dec. 2021",
            "Distributed systems", "Languages", "English (Native)",
            "Skills and Tools", "Python", "SQL",
        ])
        document = pymupdf.open()
        document.new_page().insert_text((40, 50), "\n".join(text), fontsize=11)
        for _ in range(pages - 1):
            document.new_page()
        document.save(self.pdf)
        document.close()

    def verify(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--source", str(self.source),
             "--pdf", f"en={self.pdf}"],
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


if __name__ == "__main__":
    unittest.main()
