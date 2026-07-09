#!/usr/bin/env python3
import unittest
import re
import sys
import os

# Add parent directory to path to import the update_resume module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.github/scripts')))

class TestRegexPatterns(unittest.TestCase):
    """Test the regex patterns used in the update_resume.py script."""

    def test_html_experience_pattern(self):
        """Test the regex pattern for updating experience section in HTML."""
        pattern = r'(<!-- EXPERIENCE:START -->)(.*?)(<!-- EXPERIENCE:END -->)'
        test_html = """
        <section>
            <h2>Experience</h2>
            <div>
                <!-- EXPERIENCE:START -->
                <div class="old-experience-content">This should be replaced</div>
                <!-- EXPERIENCE:END -->
            </div>
        </section>
        """

        new_content = "<div>New Experience Content</div>"
        result, count = re.subn(pattern, f'\\1\n{new_content}\n\\3', test_html, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn(new_content, result)
        self.assertNotIn("old-experience-content", result)

    def test_html_education_pattern(self):
        """Test the regex pattern for updating education section in HTML."""
        pattern = r'(<!-- EDUCATION:START -->)(.*?)(<!-- EDUCATION:END -->)'
        test_html = """
        <section>
            <h2>Education</h2>
            <div>
                <!-- EDUCATION:START -->
                <div class="old-education-content">This should be replaced</div>
                <!-- EDUCATION:END -->
            </div>
        </section>
        """

        new_content = "<div>New Education Content</div>"
        result, count = re.subn(pattern, f'\\1\n{new_content}\n\\3', test_html, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn(new_content, result)
        self.assertNotIn("old-education-content", result)

    def test_html_skills_pattern(self):
        """Test the regex pattern for updating skills section in HTML."""
        pattern = r'(<!-- SKILLS:START -->)(.*?)(<!-- SKILLS:END -->)'
        test_html = """
        <section>
            <h2>Skills</h2>
            <div>
                <!-- SKILLS:START -->
                <div class="old-skills-content">This should be replaced</div>
                <!-- SKILLS:END -->
            </div>
        </section>
        """

        new_content = "<ul><li>New Skills Content</li></ul>"
        result, count = re.subn(pattern, f'\\1\n{new_content}\n\\3', test_html, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn(new_content, result)
        self.assertNotIn("old-skills-content", result)

    def test_latex_header_pattern(self):
        """Test the regex pattern for updating the header in LaTeX files."""
        pattern = r'\\begin{tabular\*}{\\textwidth}.*?\\end{tabular\*}'
        test_latex = r"""
        \begin{tabular*}{\textwidth}
            {l@{\extracolsep{\fill}}l@{\extracolsep{6pt}}r}
            \textbf{\LARGE Old Name} & Email: & \href{mailto:old@example.com}{old@example.com} \\
            {\large Old Label} & Github: & \href{https://github.com/old}{github.com/old} \\
            & LinkedIn: & \href{https://linkedin.com/in/old}{linkedin.com/in/old} \\
        \end{tabular*}
        """

        new_content = r"""\begin{tabular*}{\textwidth}
    {l@{\extracolsep{\fill}}l@{\extracolsep{6pt}}r}
    \textbf{\LARGE New Name} & Email: & \href{mailto:new@example.com}{new@example.com} \\
    {\large New Label} & Github: & \href{https://github.com/new}{github.com/new} \\
    & LinkedIn: & \href{https://linkedin.com/in/new}{linkedin.com/in/new} \\
\end{tabular*}"""

        result, count = re.subn(pattern, lambda _: new_content, test_latex, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn("New Name", result)
        self.assertIn("new@example.com", result)
        self.assertNotIn("Old Name", result)

    def test_latex_experience_pattern(self):
        """Test the regex pattern for updating experience section in LaTeX files."""
        pattern = r'\\section{Experience}.*?\\resumeSubHeadingListStart(.*?)\\resumeSubHeadingListEnd'
        test_latex = r"""
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
        """

        new_content = r"""  \resumeSubheading
      {New Company}{New Location}
      {New Position}{Jan. 2023 - Present}
      \resumeItemListStart
        \resumeItemNoTitle
            {New Summary}
      \resumeItemListEnd
"""

        result, count = re.subn(pattern, f'\\\\section{{Experience}}\n\n\\\\resumeSubHeadingListStart\n{new_content}\\\\resumeSubHeadingListEnd', test_latex, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn("New Company", result)
        self.assertIn("New Summary", result)
        self.assertNotIn("Old Company", result)

    def test_latex_education_pattern(self):
        """Test the regex pattern for updating education section in LaTeX files."""
        pattern = r'\\section{Education}.*?\\resumeSubHeadingListStart(.*?)\\resumeSubHeadingListEnd'
        test_latex = r"""
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
        """

        new_content = r"""    \resumeSubheading
      {New University}{New Location}
      {New Degree}{Jan. 2020 -- Dec. 2023}

      \resumeItemListStart
        \resumeSubItemNoBullet
          {New course}
      \resumeItemListEnd
"""

        result, count = re.subn(pattern, f'\\\\section{{Education}}\n  \\\\resumeSubHeadingListStart\n{new_content}  \\\\resumeSubHeadingListEnd', test_latex, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn("New University", result)
        self.assertIn("New course", result)
        self.assertNotIn("Old University", result)

    def test_latex_skills_pattern(self):
        """Test the regex pattern for updating skills section in LaTeX files."""
        pattern = r'\\section{Skills \\& Competencies}.*?(?=\%-------------------------------------------)'
        test_latex = r"""
        \section{Skills \& Competencies}
         \resumeItemListStart
            \resumeItem{Old Languages}{}
            \resumeItem{Old Skills}{}
         \resumeItemListEnd

%-------------------------------------------
        """

        new_content = r""" \resumeItemListStart
    \resumeItem{New Languages}{}
    \resumeItem{New Skills}{}
 \resumeItemListEnd

"""

        result, count = re.subn(pattern, f'\\\\section{{Skills \\\\& Competencies}}\n{new_content}', test_latex, flags=re.DOTALL)

        # Test pattern matched correctly
        self.assertEqual(count, 1)
        self.assertIn("New Languages", result)
        self.assertIn("New Skills", result)
        self.assertNotIn("Old Languages", result)

    def test_edge_cases(self):
        """Test regex patterns with various edge cases."""
        # Nested sections
        html_pattern = r'(<!-- EXPERIENCE:START -->)(.*?)(<!-- EXPERIENCE:END -->)'
        nested_html = """
        <section>
            <h2>Experience</h2>
            <div>
                <!-- EXPERIENCE:START -->
                <section>
                    <div>Nested content</div>
                </section>
                <!-- EXPERIENCE:END -->
            </div>
        </section>
        """

        new_content = "<div>New nested content</div>"
        result, count = re.subn(html_pattern, f'\\1\n{new_content}\n\\3', nested_html, flags=re.DOTALL)

        # Test pattern matched correctly with nested elements
        self.assertEqual(count, 1)
        self.assertIn(new_content, result)
        self.assertNotIn("Nested content", result)

        # LaTeX with comments
        latex_pattern = r'\\section{Experience}.*?\\resumeSubHeadingListStart(.*?)\\resumeSubHeadingListEnd'
        commented_latex = r"""
        \section{Experience}
        % This is a comment
        \resumeSubHeadingListStart
          % Another comment
          \resumeSubheading
              {Old Company}{Old Location}
              {Old Position}{Jan. 2020 - Dec. 2022}
          % End comment
        \resumeSubHeadingListEnd
        """

        new_latex_content = r"""  \resumeSubheading
      {New Company}{New Location}
      {New Position}{Jan. 2023 - Present}
"""

        latex_result, count = re.subn(latex_pattern, f'\\\\section{{Experience}}\n\n\\\\resumeSubHeadingListStart\n{new_latex_content}\\\\resumeSubHeadingListEnd', commented_latex, flags=re.DOTALL)

        # Test pattern matched correctly with comments
        self.assertEqual(count, 1)
        self.assertIn("New Company", latex_result)
        self.assertNotIn("Old Company", latex_result)

if __name__ == '__main__':
    unittest.main()
