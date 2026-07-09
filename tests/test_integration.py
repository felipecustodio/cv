#!/usr/bin/env python3
import sys
import os
import unittest
import tempfile
import shutil
import yaml
import filecmp
import io
import contextlib
import importlib.util

# Add parent directory to path to import the update_resume module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.github/scripts')))

# Import the main function directly from the actual path
try:
    from .github.scripts.update_resume import main
except ImportError:
    # Alternative import path for running directly
    script_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts', 'update_resume.py')
    if os.path.exists(script_path):
        spec = importlib.util.spec_from_file_location("update_resume", script_path)
        update_resume = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(update_resume)
        main = update_resume.main
    else:
        print("Warning: Could not import update_resume.py")
        def main():
            print("Mock main function")

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment with sample files."""
        # Save the original sys.argv
        self.original_argv = sys.argv

        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Create .github/scripts directory structure in temp dir
        os.makedirs(os.path.join(self.test_dir, '.github', 'scripts'))

        # Sample YAML data
        self.yaml_data = {
            'basics': {
                'name': 'Integration Test',
                'label': 'Software Engineer',
                'email': 'integration@test.com',
                'url': 'https://test.com',
                'profiles': [
                    {
                        'network': 'GitHub',
                        'username': 'integration',
                        'url': 'https://github.com/integration'
                    },
                    {
                        'network': 'LinkedIn',
                        'username': 'integration',
                        'url': 'https://linkedin.com/in/integration'
                    }
                ]
            },
            'work': [
                {
                    'name': 'Integration Corp',
                    'url': 'https://integrationcorp.com',
                    'position': 'Test Engineer',
                    'location': 'Remote',
                    'startDate': '2023-01-01',
                    'endDate': '2025-04-30',
                    'summary': 'Integration testing',
                    'highlights': ['Wrote integration tests', 'Ensured system worked end-to-end']
                }
            ],
            'education': [
                {
                    'institution': 'Testing University',
                    'location': 'Test City',
                    'area': 'Testing',
                    'studyType': 'Master',
                    'startDate': '2020-01-01',
                    'endDate': '2022-12-31',
                    'courses': ['Advanced Testing']
                }
            ],
            'skills': [
                {
                    'name': 'Languages',
                    'keywords': ['Test Language (Native)']
                },
                {
                    'name': 'Skills and Tools',
                    'keywords': ['Testing', 'Integration', 'Python']
                }
            ]
        }

        # Create the files for testing
        self.yaml_path = os.path.join(self.test_dir, 'resume.yaml')
        with open(self.yaml_path, 'w') as f:
            yaml.dump(self.yaml_data, f)

        self.html_path = os.path.join(self.test_dir, 'index.html')
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
                        <div>Old content</div>
                        <!-- EXPERIENCE:END -->
                    </div>
                </section>
                <section>
                    <h2>Education</h2>
                    <div>
                        <!-- EDUCATION:START -->
                        <div>Old content</div>
                        <!-- EDUCATION:END -->
                    </div>
                </section>
                <section>
                    <h2>Skills</h2>
                    <div>
                        <!-- SKILLS:START -->
                        <div>Old content</div>
                        <!-- SKILLS:END -->
                    </div>
                </section>
            </body>
            </html>
            """)

        self.tex_path = os.path.join(self.test_dir, 'main.tex')
        with open(self.tex_path, 'w') as f:
            f.write(r"""
            \documentclass[letterpaper,11pt]{article}

            \begin{document}

            %----------HEADING-----------------
            \begin{tabular*}{\textwidth}
                {l@{\extracolsep{\fill}}l@{\extracolsep{6pt}}r}
                \textbf{\LARGE Old Name} & Email: & \href{mailto:old@example.com}{old@example.com} \\
                {\large Old Label} & Github: & \href{https://github.com/old}{github.com/old} \\
                & LinkedIn: & \href{https://linkedin.com/in/old}{linkedin.com/in/old} \\
            \end{tabular*}


            %-----------EXPERIENCE-----------------
            \section{Experience}

            \resumeSubHeadingListStart
              \resumeSubheading
                  {Old Company}{Old Location}
                  {Old Position}{Jan. 2020 - Dec. 2022}
                  \resumeItemListStart
                    \resumeItemNoTitle
                        {Old Summary}
                  \resumeItemListEnd
            \resumeSubHeadingListEnd

            %-----------EDUCATION-----------------
            \section{Education}
              \resumeSubHeadingListStart
                \resumeSubheading
                  {Old University}{Old Location}
                  {Old Degree}{Jan. 2015 -- Dec. 2019}

                  \resumeItemListStart
                    \resumeSubItemNoBullet
                      {Old course}
                  \resumeItemListEnd
              \resumeSubHeadingListEnd

            %-------- SKILLS------------
            \section{Skills \& Competencies}
             \resumeItemListStart
                \resumeItem{Old Skills}{}
             \resumeItemListEnd

%-------------------------------------------
            \end{document}
            """)

        # Make a copy of the script to the test directory
        self.script_path = os.path.join(self.test_dir, '.github', 'scripts', 'update_resume.py')
        original_script_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts', 'update_resume.py')
        if os.path.exists(original_script_path):
            shutil.copy(original_script_path, self.script_path)
        else:
            # Create a minimal version for testing if the original doesn't exist
            with open(self.script_path, 'w') as f:
                f.write("""
import yaml
import re
import os
from datetime import datetime

def format_date(date_str):
    if not date_str:
        return "Present"
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%b. %Y")

def load_yaml_data(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def update_html_file(data, file_path):
    with open(file_path, 'r') as file:
        html_content = file.read()

    # Simple replacement for testing
    html_content = html_content.replace('Old content', 'Updated content')

    with open(file_path, 'w') as file:
        file.write(html_content)

def update_latex_file(data, file_path):
    with open(file_path, 'r') as file:
        latex_content = file.read()

    # Simple replacement for testing
    latex_content = latex_content.replace('Old', 'New')

    with open(file_path, 'w') as file:
        file.write(latex_content)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '../..'))

    yaml_path = os.path.join(repo_root, 'resume.yaml')
    html_path = os.path.join(repo_root, 'index.html')
    tex_path = os.path.join(repo_root, 'main.tex')

    data = load_yaml_data(yaml_path)

    update_html_file(data, html_path)
    update_latex_file(data, tex_path)

    print("Updated HTML and LaTeX files successfully!")

if __name__ == "__main__":
    main()
                """)

        # Save file paths before and after modification
        self.html_before = os.path.join(self.test_dir, 'index.html.before')
        self.tex_before = os.path.join(self.test_dir, 'main.tex.before')
        shutil.copy(self.html_path, self.html_before)
        shutil.copy(self.tex_path, self.tex_before)

    def tearDown(self):
        """Clean up after tests."""
        # Restore original sys.argv
        sys.argv = self.original_argv

        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def capture_output(self, func, *args, **kwargs):
        """Capture stdout output from a function call."""
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            func(*args, **kwargs)
        return captured_output.getvalue()

    def test_main_function(self):
        """Test that the main function correctly updates both files."""
        # Change working directory to test directory
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        try:
            # Monkey patch os.path.abspath to return test directory paths
            original_abspath = os.path.abspath
            def mock_abspath(path):
                if path.endswith('../..'):
                    return self.test_dir
                return original_abspath(path)

            os.path.abspath = mock_abspath

            # Run the main function
            output = self.capture_output(main)

            # Restore original abspath
            os.path.abspath = original_abspath

            # Check that the output indicates success
            self.assertIn("Updated HTML and LaTeX files successfully", output)

            # Check that files were modified
            self.assertFalse(filecmp.cmp(self.html_path, self.html_before), "HTML file should be modified")
            self.assertFalse(filecmp.cmp(self.tex_path, self.tex_before), "LaTeX file should be modified")

            # Check specific content in files
            with open(self.html_path, 'r') as f:
                html_content = f.read()
            self.assertNotIn('Old content', html_content)
            self.assertEqual(html_content.count("Integration Corp"), 1)
            self.assertEqual(html_content.count("Testing University"), 1)

            with open(self.tex_path, 'r') as f:
                tex_content = f.read()
            self.assertNotIn('Old Name', tex_content)
            self.assertNotIn('Old Label', tex_content)
            self.assertEqual(tex_content.count(r"\section{Experience}"), 1)
            self.assertEqual(tex_content.count("Integration Corp"), 1)

        finally:
            # Change back to original directory
            os.chdir(original_cwd)

if __name__ == '__main__':
    unittest.main()
