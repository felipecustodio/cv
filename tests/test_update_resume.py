#!/usr/bin/env python3
import sys
import os
import unittest
import tempfile
import shutil
import yaml

# Add parent directory to path to import the update_resume module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.github/scripts')))

# Import directly from the script
from update_resume import (
    build_degree_text,
    escape_latex,
    format_date,
    load_yaml_data,
    update_html_file,
    update_latex_file,
)

class TestResumeUpdate(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures, creating test files and directories."""
        self.test_dir = tempfile.mkdtemp()

        # Create a sample YAML file
        self.yaml_data = {
            'basics': {
                'name': 'Test Name',
                'label': 'Test Label',
                'email': 'test@example.com',
                'url': 'https://example.com',
                'profiles': [
                    {
                        'network': 'GitHub',
                        'username': 'testuser',
                        'url': 'https://github.com/testuser'
                    },
                    {
                        'network': 'LinkedIn',
                        'username': 'testuser',
                        'url': 'https://linkedin.com/in/testuser'
                    }
                ]
            },
            'work': [
                {
                    'name': 'Test Company',
                    'url': 'https://testcompany.com',
                    'position': 'Test Position',
                    'location': 'Test Location',
                    'startDate': '2020-01-01',
                    'endDate': '2022-12-31',
                    'summary': 'Test summary',
                    'highlights': [
                        'Test highlight 1',
                        'Test highlight 2'
                    ]
                }
            ],
            'education': [
                {
                    'institution': 'Test University',
                    'url': 'https://university.example',
                    'englishUrl': 'https://university-example.translate.goog/?_x_tr_sl=pt&_x_tr_tl=en',
                    'location': 'Test Location',
                    'area': 'Computer Science',
                    'studyType': 'Bachelor',
                    'startDate': '2015-01-01',
                    'endDate': '2019-12-31',
                    'courses': [
                        'Test course description'
                    ]
                }
            ],
            'skills': [
                {
                    'name': 'Languages',
                    'keywords': ['English (Native)', 'Spanish (Fluent)']
                },
                {
                    'name': 'Skills and Tools',
                    'keywords': ['Python', 'JavaScript', 'Git']
                }
            ]
        }

        self.yaml_path = os.path.join(self.test_dir, 'test_resume.yaml')
        with open(self.yaml_path, 'w') as f:
            yaml.dump(self.yaml_data, f)

        # Create sample HTML file
        self.html_path = os.path.join(self.test_dir, 'test_index.html')
        with open(self.html_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Resume</title>
            </head>
            <body>
                <section>
                    <h2>Experience</h2>
                    <div>
                        <!-- EXPERIENCE:START -->
                        <div>Experience content will be replaced here</div>
                        <!-- EXPERIENCE:END -->
                    </div>
                </section>
                <section>
                    <h2>Education</h2>
                    <div>
                        <!-- EDUCATION:START -->
                        <div>Education content will be replaced here</div>
                        <!-- EDUCATION:END -->
                    </div>
                </section>
                <section>
                    <h2>Skills</h2>
                    <div>
                        <!-- SKILLS:START -->
                        <div>Skills content will be replaced here</div>
                        <!-- SKILLS:END -->
                    </div>
                </section>
            </body>
            </html>
            """)

        # Create sample LaTeX file
        self.tex_path = os.path.join(self.test_dir, 'test_main.tex')
        with open(self.tex_path, 'w') as f:
            f.write(r"""
            \documentclass[letterpaper,11pt]{article}

            \begin{document}

            %----------HEADING-----------------
            % HEADER:START
            \begin{tabular*}{\textwidth}
                {l@{\extracolsep{\fill}}l@{\extracolsep{6pt}}r}
                \textbf{\LARGE Name} & Email: & \href{mailto:email@example.com}{email@example.com} \\
                {\large Label} & Github: & \href{https://github.com/user}{github.com/user} \\
                & LinkedIn: & \href{https://linkedin.com/in/user}{linkedin.com/in/user} \\
            \end{tabular*}
            % HEADER:END


            %-----------EXPERIENCE-----------------
            \section{Experience}

            % EXPERIENCE:START
            \resumeSubHeadingListStart
              \resumeSubheading
                  {Company}{Location}
                  {Position}{Jan. 2020 - Dec. 2022}
                  \resumeItemListStart
                    \resumeItemNoTitle
                        {Summary}
                    \resumeItemNoTitle
                        {Highlight 1}
                    \resumeItemNoTitle
                        {Highlight 2}
                  \resumeItemListEnd
            \resumeSubHeadingListEnd
            % EXPERIENCE:END

            %-----------EDUCATION-----------------
            \section{Education}
              % EDUCATION:START
              \resumeSubHeadingListStart
                \resumeSubheading
                  {University}{Location}
                  {Degree}{Jan. 2015 -- Dec. 2019}

                  \resumeItemListStart
                    \resumeSubItemNoBullet
                      {Course description}
                  \resumeItemListEnd
              \resumeSubHeadingListEnd
              % EDUCATION:END

            %-------- SKILLS------------
            \section{Skills \& Competencies}
              % SKILLS:START
              \resumeItemListStart
                 \resumeItem{Languages}{}
                 \resumeItem{Skills and Tools}{}
              \resumeItemListEnd
              % SKILLS:END

%-------------------------------------------
            \end{document}
            """)

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(self.test_dir)

    def test_format_date(self):
        """Test the format_date function."""
        self.assertEqual(format_date('2022-01-01'), 'Jan. 2022')
        self.assertEqual(format_date('2020-12-31'), 'Dec. 2020')
        self.assertEqual(format_date(None), 'Present')
        self.assertEqual(format_date(''), 'Present')

    def test_load_yaml_data(self):
        """Test loading YAML data from a file."""
        data = load_yaml_data(self.yaml_path)
        self.assertEqual(data['basics']['name'], 'Test Name')
        self.assertEqual(len(data['work']), 1)
        self.assertEqual(len(data['education']), 1)
        self.assertEqual(len(data['skills']), 2)

    def test_update_html_file(self):
        """Test updating an HTML file with YAML data."""
        data = load_yaml_data(self.yaml_path)
        update_html_file(data, self.html_path)

        # Read the updated HTML file
        with open(self.html_path, 'r') as f:
            content = f.read()

        # Check that the content has been updated
        self.assertIn('Test Company', content)
        self.assertIn('Test Position', content)
        self.assertIn('Test University', content)
        self.assertIn('https://university.example', content)
        self.assertIn('https://university-example.translate.goog/?_x_tr_sl=pt&amp;_x_tr_tl=en', content)
        self.assertIn('[English]', content)
        self.assertIn('Test course description', content)
        self.assertIn('English (Native)', content)
        self.assertIn('Python', content)
        self.assertEqual(content.count("Test Company"), 1)
        self.assertNotIn("Experience content will be replaced here", content)
        self.assertNotIn(r"\1", content)
        self.assertNotIn(r"\3", content)
        self.assertIn("<!-- EXPERIENCE:START -->", content)
        self.assertIn("<!-- EXPERIENCE:END -->", content)
        self.assertIn("<!-- EDUCATION:START -->", content)
        self.assertIn("<!-- EDUCATION:END -->", content)
        self.assertIn("<!-- SKILLS:START -->", content)
        self.assertIn("<!-- SKILLS:END -->", content)

    def test_update_latex_file(self):
        """Test updating a LaTeX file with YAML data."""
        data = load_yaml_data(self.yaml_path)
        update_latex_file(data, self.tex_path)

        # Read the updated LaTeX file
        with open(self.tex_path, 'r') as f:
            content = f.read()

        # Check that the content has been updated - the names should be there regardless of escaping
        self.assertIn('Test Name', content)
        self.assertIn('Test Company', content)
        self.assertIn('Test Position', content)
        self.assertIn('Jan. 2020 - Dec. 2022', content)
        self.assertIn('Test University', content)
        self.assertIn('https://university.example', content)
        self.assertIn('https://university-example.translate.goog/?\\_x\\_tr\\_sl=pt\\&\\_x\\_tr\\_tl=en', content)
        self.assertIn('[English]', content)
        self.assertIn('Test course description', content)

        # For language-related checks, we need to check either with or without escaping
        # as the implementation could use either approach
        self.assertTrue('English' in content and 'Native' in content)
        self.assertTrue('Python | JavaScript | Git' in content)

    def test_update_html_file_raises_when_marker_missing(self):
        """Missing template markers should fail fast instead of silently skipping."""
        with open(self.html_path, "w") as f:
            f.write("<html><body><section><h2>No expected markers</h2></section></body></html>")

        with self.assertRaises(ValueError):
            update_html_file(self.yaml_data, self.html_path)

    def test_update_latex_file_raises_when_marker_missing(self):
        """Missing LaTeX section markers should raise an explicit error."""
        with open(self.tex_path, "w") as f:
            f.write(r"\documentclass{article}\begin{document}\section{NoMarkers}\end{document}")

        with self.assertRaises(ValueError):
            update_latex_file(self.yaml_data, self.tex_path)

    def test_escape_latex(self):
        """LaTeX special characters should be escaped safely."""
        raw = r"_ % & # $ { } ~ ^ \\"
        escaped = escape_latex(raw)
        self.assertIn(r"\_", escaped)
        self.assertIn(r"\%", escaped)
        self.assertIn(r"\&", escaped)
        self.assertIn(r"\#", escaped)
        self.assertIn(r"\$", escaped)
        self.assertIn(r"\{", escaped)
        self.assertIn(r"\}", escaped)
        self.assertIn(r"\~{}", escaped)
        self.assertIn(r"\^{}", escaped)
        self.assertIn(r"\textbackslash{}", escaped)

    def test_update_latex_file_escapes_user_content(self):
        """User-provided LaTeX special characters should be escaped in output."""
        self.yaml_data["basics"]["name"] = "Name_One"
        self.yaml_data["work"][0]["summary"] = "Saved 50% & reduced cost #1"
        self.yaml_data["education"][0]["courses"] = [r"Path C:\tools"]

        update_latex_file(self.yaml_data, self.tex_path)

        with open(self.tex_path, "r") as f:
            content = f.read()

        self.assertIn(r"Name\_One", content)
        self.assertIn(r"50\% \& reduced cost \#1", content)
        self.assertIn(r"\textbackslash{}tools", content)

    def test_build_degree_text(self):
        """Degree rendering should prefer explicit value and fallback sensibly."""
        self.assertEqual(
            build_degree_text({"degree": "Master of Engineering"}),
            "Master of Engineering",
        )
        self.assertEqual(
            build_degree_text({"studyType": "Bachelor", "area": "Computer Science"}),
            "Bachelor in Computer Science",
        )
        self.assertEqual(build_degree_text({"studyType": "PhD"}), "PhD")
        self.assertEqual(build_degree_text({"area": "Design"}), "Design")

    def test_update_outputs_use_data_driven_degree(self):
        """HTML and LaTeX should render degree text from YAML data."""
        self.yaml_data["education"][0]["degree"] = "Master of Science in AI"
        update_html_file(self.yaml_data, self.html_path)
        update_latex_file(self.yaml_data, self.tex_path)

        with open(self.html_path, "r") as f:
            html_content = f.read()
        with open(self.tex_path, "r") as f:
            tex_content = f.read()

        self.assertIn("Master of Science in AI", html_content)
        self.assertIn("Master of Science in AI", tex_content)

    def test_empty_yaml_data(self):
        """Test handling of empty YAML data."""
        empty_yaml_path = os.path.join(self.test_dir, 'empty.yaml')
        with open(empty_yaml_path, 'w') as f:
            f.write('{}')

        data = load_yaml_data(empty_yaml_path)

        # Should not raise errors when updating with empty data
        update_html_file(data, self.html_path)
        update_latex_file(data, self.tex_path)

        # Check that the files still exist
        self.assertTrue(os.path.exists(self.html_path))
        self.assertTrue(os.path.exists(self.tex_path))


if __name__ == '__main__':
    unittest.main()
