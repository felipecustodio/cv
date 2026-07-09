#!/usr/bin/env python3
import os
import re
import html
from datetime import datetime
import yaml


HTML_WORK_TEMPLATE = '''
        <article class="entry-card">
            <div class="entry-header">{logo_html}
                <div class="entry-header-text">
                    <h3 class="entry-title">{heading_content}</h3>
                    <p class="entry-role">{position}</p>
                    <p class="entry-meta">{location} | {start_date} - {end_date}</p>
                </div>
            </div>
            <ul class="entry-list">
                <li>{summary}</li>
                {highlights_html}
            </ul>
        </article>
'''

HTML_EDUCATION_TEMPLATE = '''
        <article class="entry-card entry-card--education">
            <div class="entry-header">{logo_html}
                <div class="entry-header-text">
                    <h3 class="entry-title">{heading_content}</h3>
                    <p class="entry-role">{degree_type}</p>
                    <p class="entry-meta">{location} | {start_date} - {end_date}</p>
                </div>
            </div>
            <ul class="entry-list">
                {courses_html}
            </ul>
        </article>
'''


def escape_latex(value):
    """Escape LaTeX-special characters in user-provided content."""
    if value is None:
        return ""

    text = str(value)
    replacements = {
        "\\": r"\\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "^": r"\^{}",
        "~": r"\~{}",
    }
    return re.sub(r"[\\{}$&%#_^~]", lambda match: replacements[match.group(0)], text)


def escape_html(value):
    """Escape HTML-special characters in user-provided content."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def replace_section_or_raise(content, pattern, replacement_fn, section_name):
    """Replace one section and fail if template markers are missing or duplicated."""
    if isinstance(replacement_fn, str):
        repl = lambda _: replacement_fn
    else:
        repl = replacement_fn
    updated, count = re.subn(pattern, repl, content, flags=re.DOTALL)
    if count != 1:
        raise ValueError(
            f"Could not uniquely update {section_name}; expected 1 match, found {count}."
        )
    return updated


def build_degree_text(education_item):
    """Build degree text from explicit YAML value first, then sensible fallbacks."""
    explicit_degree = education_item.get("degree")
    if explicit_degree:
        return str(explicit_degree)

    study_type = education_item.get("studyType")
    area = education_item.get("area")
    if study_type and area:
        return f"{study_type} in {area}"
    if study_type:
        return str(study_type)
    if area:
        return str(area)
    return ""


def format_date(date_str):
    """Format date from YYYY-MM-DD to Month Year"""
    if not date_str:
        return "Present"

    # Handle the case when date_str is already a datetime.date object
    if isinstance(date_str, datetime):
        date_obj = date_str
    elif isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        # If it's another type (like date), convert to string then parse
        try:
            date_obj = datetime.combine(date_str, datetime.min.time())
        except Exception:
            # If all else fails, return as is
            return str(date_str)

    return date_obj.strftime("%b. %Y")

def load_yaml_data(file_path):
    """Load data from resume.yaml file"""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def update_html_file(data, file_path):
    """Update the HTML file with data from YAML"""
    with open(file_path, 'r') as file:
        html_content = file.read()

    # Update experience section
    work_html = ""
    for job in data.get('work', []):
        start_date = escape_html(format_date(job.get('startDate')))
        end_date = escape_html(format_date(job.get('endDate')))

        highlights_html = ""
        for highlight in job.get('highlights', []):
            highlights_html += f'                <li>{escape_html(highlight)}</li>\n'

        job_name = escape_html(job.get('name', ''))
        job_url = job.get('url')
        if job_url:
            heading_content = f'<a href="{escape_html(job_url)}" target="_blank" rel="noopener" class="company-link">{job_name}</a>'
        else:
            heading_content = job_name

        logo_path = job.get('logo')
        if logo_path:
            logo_html = f'''
            <div class="entry-logo">
                <img src="{escape_html(logo_path)}" alt="{job_name} logo">
            </div>'''
        else:
            logo_html = ''

        work_html += HTML_WORK_TEMPLATE.format(
            logo_html=logo_html,
            heading_content=heading_content,
            position=escape_html(job.get('position', '')),
            location=escape_html(job.get('location', '')),
            start_date=start_date,
            end_date=end_date,
            summary=escape_html(job.get('summary', '')),
            highlights_html=highlights_html
        )

    # Update education section
    education_html = ""
    for edu in data.get('education', []):
        start_date = escape_html(format_date(edu.get('startDate')))
        end_date = escape_html(format_date(edu.get('endDate')))

        courses_html = ""
        for course in edu.get('courses', []):
            courses_html += f'                <li>{escape_html(course)}</li>\n'

        degree_type = escape_html(build_degree_text(edu))

        edu_name = escape_html(edu.get('institution', ''))
        edu_url = edu.get('url')
        if edu_url:
            heading_content = f'<a href="{escape_html(edu_url)}" target="_blank" rel="noopener" class="company-link">{edu_name}</a>'
        else:
            heading_content = edu_name

        logo_path = edu.get('logo')
        if logo_path:
            logo_html = f'''
            <div class="entry-logo">
                <img src="{escape_html(logo_path)}" alt="{edu_name} logo">
            </div>'''
        else:
            logo_html = ''

        education_html += HTML_EDUCATION_TEMPLATE.format(
            logo_html=logo_html,
            heading_content=heading_content,
            degree_type=degree_type,
            location=escape_html(edu.get('location', '')),
            start_date=start_date,
            end_date=end_date,
            courses_html=courses_html
        )

    # Update skills section
    skills_html = "<ul class=\"skills-list\">\n"
    for skill in data.get('skills', []):
        skill_name = escape_html(skill.get("name", "Skills"))
        keywords = ", ".join(escape_html(keyword) for keyword in skill.get("keywords", []))
        if skill_name == "Languages":
            skills_html += f'    <li><span class="skills-label">Languages</span> {keywords}</li>\n'
        else:
            skills_html += f'    <li><span class="skills-label">{skill_name}</span> {keywords}</li>\n'
    skills_html += "</ul>"

    # Replace content in HTML using regex patterns
    # Experience section
    html_content = replace_section_or_raise(
        html_content,
        r'(<!-- EXPERIENCE:START -->)(.*?)(<!-- EXPERIENCE:END -->)',
        lambda m: f'{m.group(1)}\n{work_html}\n        {m.group(3)}',
        "HTML experience section",
    )

    # Education section
    html_content = replace_section_or_raise(
        html_content,
        r'(<!-- EDUCATION:START -->)(.*?)(<!-- EDUCATION:END -->)',
        lambda m: f'{m.group(1)}\n{education_html}\n        {m.group(3)}',
        "HTML education section",
    )

    # Skills section
    html_content = replace_section_or_raise(
        html_content,
        r'(<!-- SKILLS:START -->)(.*?)(<!-- SKILLS:END -->)',
        lambda m: f'{m.group(1)}\n{skills_html}\n        {m.group(3)}',
        "HTML skills section",
    )

    # Write updated content back to file
    with open(file_path, 'w') as file:
        file.write(html_content)

def update_latex_file(data, file_path):
    """Update the LaTeX file with data from YAML"""
    with open(file_path, 'r') as file:
        latex_content = file.read()

    # Update name and contact information
    basics = data.get('basics', {})
    name = escape_latex(basics.get('name', ''))
    label = escape_latex(basics.get('label', ''))
    email = escape_latex(basics.get('email', ''))
    github_profile = next((p for p in basics.get('profiles', []) if p.get('network') == 'GitHub'), {})
    linkedin_profile = next((p for p in basics.get('profiles', []) if p.get('network') == 'LinkedIn'), {})
    github_url = escape_latex(github_profile.get('url', ''))
    github_username = escape_latex(github_profile.get('username', ''))
    linkedin_url = escape_latex(linkedin_profile.get('url', ''))
    linkedin_username = escape_latex(linkedin_profile.get('username', ''))

    # Update header section with proper escaping for LaTeX
    header_latex = f'''\\textbf{{\\LARGE {name}}}
& Email: & \\href{{mailto:{email}}}{{{email}}} \\\\
{{\\large {label}}}
& Github: & \\href{{{github_url}}}{{github.com/{github_username}}} \\\\
& LinkedIn: & \\href{{{linkedin_url}}}{{linkedin.com/in/{linkedin_username}}} \\\\'''

    # Update the header in the LaTeX file with proper escaping
    header_table = f'''\\begin{{tabular*}}{{\\textwidth}}
    {{
    l@{{\\extracolsep{{\\fill}}}}l
    @{{\\extracolsep{{6pt}}}}r
    l@{{\\extracolsep{{\\fill}}}}l
    @{{\\extracolsep{{6pt}}}}r
    @{{\\extracolsep{{6pt}}}}r
    @{{\\extracolsep{{6pt}}}}r
    }}

{header_latex}

\\end{{tabular*}}'''

    latex_content = replace_section_or_raise(
        latex_content,
        r'(\% HEADER:START\s*)(.*?)(\s*\% HEADER:END)',
        lambda m: f'{m.group(1)}{header_table}{m.group(3)}',
        "LaTeX header table",
    )

    # Update experience section
    work_latex = ""
    for job in data.get('work', []):
        start_date = format_date(job.get('startDate'))
        end_date = format_date(job.get('endDate'))
        job_name = escape_latex(job.get('name', ''))
        job_url_raw = job.get('url', '')
        job_url = escape_latex(job_url_raw)
        url_domain = escape_latex(job_url_raw.replace('https://', '').replace('http://', '').rstrip('/'))
        position = escape_latex(job.get('position', ''))
        location = escape_latex(job.get('location', ''))
        summary = escape_latex(job.get('summary', ''))

        work_latex += f'''  \\resumeSubheading
      {{{job_name} \\href{{{job_url}}}{{{url_domain}}}}}{{{location}}}
      {{{position}}}{{{start_date} - {end_date}}}
      \\resumeItemListStart
        \\resumeItemNoTitle
            {{{summary}}}
'''

        for highlight in job.get('highlights', []):
            work_latex += f'''        \\resumeItemNoTitle
            {{{escape_latex(highlight)}}}
'''

        work_latex += '''      \\resumeItemListEnd
'''

    # Update the experience section in the LaTeX file
    latex_content = replace_section_or_raise(
        latex_content,
        r'(\% EXPERIENCE:START\s*)(.*?)(\s*\% EXPERIENCE:END)',
        lambda m: f'{m.group(1)}\\resumeSubHeadingListStart\n{work_latex}  \\resumeSubHeadingListEnd{m.group(3)}',
        "LaTeX experience section",
    )

    # Update education section
    education_latex = ""
    for edu in data.get('education', []):
        start_date = format_date(edu.get('startDate'))
        end_date = format_date(edu.get('endDate'))
        institution = escape_latex(edu.get('institution', ''))
        location = escape_latex(edu.get('location', ''))
        degree = escape_latex(build_degree_text(edu))

        edu_url_raw = edu.get('url', '')
        if edu_url_raw:
            edu_url = escape_latex(edu_url_raw)
            url_domain = escape_latex(edu_url_raw.replace('https://', '').replace('http://', '').rstrip('/'))
            institution_text = f'{institution} \\href{{{edu_url}}}{{{url_domain}}}'
        else:
            institution_text = institution

        education_latex += f'''    \\resumeSubheading
      {{{institution_text}}}{{{location}}}
      {{{degree} }}{{{start_date} -- {end_date}}}

      \\resumeItemListStart
'''

        for course in edu.get('courses', []):
            education_latex += f'''        \\resumeSubItemNoBullet
          {{{escape_latex(course)}}}
'''

        education_latex += '''      \\resumeItemListEnd

'''

    # Update the education section in the LaTeX file
    latex_content = replace_section_or_raise(
        latex_content,
        r'(\% EDUCATION:START\s*)(.*?)(\s*\% EDUCATION:END)',
        lambda m: f'{m.group(1)}\\resumeSubHeadingListStart\n{education_latex}  \\resumeSubHeadingListEnd{m.group(3)}',
        "LaTeX education section",
    )

    # Update skills section
    skills_latex = " \\resumeItemListStart\n"

    for skill in data.get('skills', []):
        skill_name = escape_latex(skill.get('name'))
        keywords = skill.get('keywords', [])

        if skill_name == "Languages":
            skills_latex += f'''    \\resumeItem{{{skill_name}}}{{}}\\vspace{{-3pt}}{{
        \\resumeItemListStart
'''
            for language in keywords:
                parts = language.split("(")
                if len(parts) > 1:
                    lang_name = escape_latex(parts[0].strip())
                    lang_level = escape_latex(f"({parts[1]}")
                    skills_latex += f'''            \\resumeItem{{{lang_name}}}{{{lang_level}}}
'''
                else:
                    skills_latex += f'''            \\resumeItem{{{escape_latex(language)}}}{{}}
'''

            skills_latex += '''        \\resumeItemListEnd
    }
'''
        else:
            escaped_keywords = [escape_latex(keyword) for keyword in keywords]
            skills_latex += f'''    \\resumeItem{{{skill_name}}}{{}}\\vspace{{-3pt}}{{
        \\resumeItemListStart
            \\resumeItemNoTitle
            {{{' | '.join(escaped_keywords)}}}
        \\resumeItemListEnd
    }}
'''

    skills_latex += " \\resumeItemListEnd\n"

    # Update the skills section in the LaTeX file
    latex_content = replace_section_or_raise(
        latex_content,
        r'(\% SKILLS:START\s*)(.*?)(\s*\% SKILLS:END)',
        lambda m: f'{m.group(1)}{skills_latex}{m.group(3)}',
        "LaTeX skills section",
    )

    # Write updated content back to file
    with open(file_path, 'w') as file:
        file.write(latex_content)

def main():
    """Main function to update HTML and LaTeX files from YAML data"""
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
