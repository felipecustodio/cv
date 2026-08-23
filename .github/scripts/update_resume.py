#!/usr/bin/env python3
import os
import re
import html
import copy
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


DEFAULT_STRINGS = {
    "pageTitle": "CV",
    "utilityNavigation": "Utility links",
    "home": "Home",
    "downloadPdf": "Download PDF",
    "switchToDarkMode": "Switch to dark mode",
    "switchToLightMode": "Switch to light mode",
    "darkMode": "Dark mode",
    "lightMode": "Light mode",
    "languageMenu": "Language",
    "curriculumVitae": "Curriculum Vitae",
    "email": "Email",
    "github": "GitHub",
    "linkedin": "LinkedIn",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "languages": "Languages",
    "skillsAndTools": "Skills and Tools",
}


def localized_value(value, locale, fallback_locale="en"):
    """Return a locale-specific value while supporting the legacy scalar schema."""
    if not isinstance(value, dict):
        return value
    return value.get(locale, value.get(fallback_locale, next(iter(value.values()), "")))


def get_locales(data):
    """Return configured locales in YAML order, with a legacy English fallback."""
    locales = data.get("site", {}).get("locales", {})
    if locales:
        return locales
    return {"en": {"label": "English", "directory": "."}}


def get_locale_strings(data, locale):
    """Return translated interface strings with safe English fallbacks."""
    strings = DEFAULT_STRINGS.copy()
    strings.update(data.get("strings", {}).get("en", {}))
    strings.update(data.get("strings", {}).get(locale, {}))
    return strings


def localize_resume_data(data, locale):
    """Resolve localized leaf values into the shape consumed by both renderers."""
    localized = copy.deepcopy(data)
    basics = localized.setdefault("basics", {})
    basics["label"] = localized_value(basics.get("label", ""), locale)

    for job in localized.get("work", []):
        for field in ("location", "position", "summary"):
            job[field] = localized_value(job.get(field, ""), locale)
        job["highlights"] = localized_value(job.get("highlights", []), locale)

    for education in localized.get("education", []):
        for field in ("institution", "location", "area", "studyType", "degree"):
            if field in education:
                education[field] = localized_value(education[field], locale)
        education["courses"] = localized_value(education.get("courses", []), locale)

    for skill in localized.get("skills", []):
        skill["_is_languages"] = localized_value(skill.get("name", ""), "en") == "Languages"
        skill["name"] = localized_value(skill.get("name", "Skills"), locale)
        skill["keywords"] = localized_value(skill.get("keywords", []), locale)

    return localized


def replace_marker(content, start_marker, end_marker, replacement, section_name):
    """Replace an optional persistent marker pair, preserving markers for future runs."""
    pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
    updated, count = re.subn(
        pattern,
        lambda _: f"{start_marker}\n{replacement}\n{end_marker}",
        content,
        flags=re.DOTALL,
    )
    if count > 1:
        raise ValueError(f"Could not uniquely update {section_name}; found {count} marker pairs.")
    return updated


def replace_attribute(content, selector_pattern, attribute, value):
    """Replace an attribute in one generated element when the template includes it."""
    pattern = rf"({selector_pattern}[^>]*\s{re.escape(attribute)}=\")([^\"]*)(\")"
    return re.sub(pattern, lambda match: f"{match.group(1)}{escape_html(value)}{match.group(3)}", content, count=1)


def locale_directory(data, locale):
    """Return the output directory configured for a locale."""
    return get_locales(data).get(locale, {}).get("directory", locale)


def locale_link(data, current_locale, target_locale):
    """Build a relative link between generated locale directories."""
    current_directory = locale_directory(data, current_locale)
    target_directory = locale_directory(data, target_locale)
    if current_directory == target_directory:
        return "./"
    if current_directory == ".":
        return f"{target_directory.rstrip('/')}/"
    if target_directory == ".":
        return "../"
    return f"../{target_directory.rstrip('/')}/"


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


def format_date(date_str, locale="en"):
    """Format date from YYYY-MM-DD to Month Year"""
    if not date_str:
        return "Presente" if locale == "pt-BR" else "Present"

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

    if locale == "pt-BR":
        months = ["jan.", "fev.", "mar.", "abr.", "mai.", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
        return f"{months[date_obj.month - 1]} {date_obj.year}"
    return date_obj.strftime("%b. %Y")

def load_yaml_data(file_path):
    """Load data from resume.yaml file"""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def update_html_file(data, file_path, locale="en", asset_prefix="", template_content=None):
    """Update the HTML file with data from YAML"""
    if template_content is None:
        with open(file_path, 'r') as file:
            html_content = file.read()
    else:
        html_content = template_content

    localized_data = localize_resume_data(data, locale)
    strings = get_locale_strings(data, locale)
    basics = localized_data.get("basics", {})

    html_content = re.sub(
        r'(<html\s+lang=")[^"]*("\s+data-locale=")[^"]*(")',
        lambda match: f'{match.group(1)}{escape_html(locale)}{match.group(2)}{escape_html(locale)}{match.group(3)}',
        html_content,
        count=1,
    )
    html_content = re.sub(
        r"<title>.*?</title>",
        f"<title>{escape_html(basics.get('name', ''))} - {escape_html(strings['pageTitle'])}</title>",
        html_content,
        count=1,
        flags=re.DOTALL,
    )
    html_content = replace_attribute(html_content, r'<nav class="utility-nav"', "aria-label", strings["utilityNavigation"])
    html_content = replace_attribute(html_content, r'<button class="theme-toggle"', "aria-label", strings["switchToDarkMode"])
    html_content = replace_attribute(html_content, r'<button class="language-picker__trigger"', "aria-label", strings["languageMenu"])
    html_content = replace_attribute(html_content, r'<button class="language-picker__trigger"', "data-label", strings["languageMenu"])
    for attribute, key in (
        ("data-label-dark", "darkMode"),
        ("data-label-light", "lightMode"),
        ("data-switch-dark", "switchToDarkMode"),
        ("data-switch-light", "switchToLightMode"),
    ):
        html_content = replace_attribute(html_content, r'<button class="theme-toggle"', attribute, strings[key])

    for key, value in (
        ("HOME", strings["home"]),
        ("DOWNLOAD_PDF", strings["downloadPdf"]),
        ("THEME_MODE", strings["darkMode"]),
        ("LANGUAGE_MENU", strings["languageMenu"]),
        ("CURRICULUM_VITAE", strings["curriculumVitae"]),
        ("NAME", basics.get("name", "")),
        ("ROLE", basics.get("label", "")),
        ("EMAIL", strings["email"]),
        ("GITHUB", strings["github"]),
        ("LINKEDIN", strings["linkedin"]),
        ("EXPERIENCE", strings["experience"]),
        ("EDUCATION", strings["education"]),
        ("SKILLS", strings["skills"]),
    ):
        html_content = replace_marker(
            html_content,
            f"<!-- UI:{key}:START -->",
            f"<!-- UI:{key}:END -->",
            escape_html(value),
            f"HTML {key.lower()} label",
        )

    language_switcher = '<div class="language-picker">\n'
    language_switcher += f'                <button class="language-picker__trigger" type="button" aria-expanded="false" aria-controls="language-options" aria-label="{escape_html(strings["languageMenu"])}">\n'
    language_switcher += f'                    <span class="language-picker__current">{escape_html(get_locales(data).get(locale, {}).get("label", locale))}</span>\n'
    language_switcher += '                    <span class="language-picker__arrow" aria-hidden="true"></span>\n'
    language_switcher += '                </button>\n'
    language_switcher += '                <div class="language-picker__menu" id="language-options" hidden>\n'
    for language_code, language_config in get_locales(data).items():
        language_label = language_config.get("label", language_code)
        current_attribute = ' aria-current="page"' if language_code == locale else ''
        href = locale_link(data, locale, language_code)
        language_switcher += f'                    <a href="{escape_html(href)}"{current_attribute}>{escape_html(language_label)}</a>\n'
    language_switcher += '                </div>\n            </div>'
    html_content = replace_marker(
        html_content,
        "<!-- LANGUAGE_SWITCHER:START -->",
        "<!-- LANGUAGE_SWITCHER:END -->",
        language_switcher,
        "HTML language switcher",
    )
    html_content = re.sub(
        r'(<a class="action-button" href=")[^"]*(" download="[^>]*>)',
        lambda match: f'{match.group(1)}resume.pdf{match.group(2)}',
        html_content,
        count=1,
    )

    # Update experience section
    work_html = ""
    for job in localized_data.get('work', []):
        start_date = escape_html(format_date(job.get('startDate'), locale))
        end_date = escape_html(format_date(job.get('endDate'), locale))

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
            if not re.match(r'^[a-z]+://', logo_path):
                logo_path = f"{asset_prefix}{logo_path}"
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
    for edu in localized_data.get('education', []):
        start_date = escape_html(format_date(edu.get('startDate'), locale))
        end_date = escape_html(format_date(edu.get('endDate'), locale))

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
            if not re.match(r'^[a-z]+://', logo_path):
                logo_path = f"{asset_prefix}{logo_path}"
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
    for skill in localized_data.get('skills', []):
        skill_name = escape_html(skill.get("name", "Skills"))
        keywords = ", ".join(escape_html(keyword) for keyword in skill.get("keywords", []))
        if skill.get("_is_languages"):
            skills_html += f'    <li><span class="skills-label">{escape_html(strings["languages"])}</span> {keywords}</li>\n'
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

def update_latex_file(data, file_path, locale="en", template_content=None):
    """Update the LaTeX file with data from YAML"""
    if template_content is None:
        with open(file_path, 'r') as file:
            latex_content = file.read()
    else:
        latex_content = template_content

    localized_data = localize_resume_data(data, locale)
    strings = get_locale_strings(data, locale)

    # Update name and contact information
    basics = localized_data.get('basics', {})
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
& {escape_latex(strings["email"])}: & \\href{{mailto:{email}}}{{{email}}} \\\\
{{\\large {label}}}
& {escape_latex(strings["github"])}: & \\href{{{github_url}}}{{github.com/{github_username}}} \\\\
& {escape_latex(strings["linkedin"])}: & \\href{{{linkedin_url}}}{{linkedin.com/in/{linkedin_username}}} \\\\'''

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
        r'(\% HEADER:START)(.*?)(\% HEADER:END)',
        lambda m: f'{m.group(1)}\n{header_table}\n{m.group(3)}',
        "LaTeX header table",
    )

    # Update experience section
    work_latex = ""
    for job in localized_data.get('work', []):
        start_date = format_date(job.get('startDate'), locale)
        end_date = format_date(job.get('endDate'), locale)
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
        r'(\% EXPERIENCE:START)(.*?)(\% EXPERIENCE:END)',
        lambda m: f'{m.group(1)}\n  \\resumeSubHeadingListStart\n{work_latex}  \\resumeSubHeadingListEnd\n  {m.group(3)}',
        "LaTeX experience section",
    )

    # Update education section
    education_latex = ""
    for edu in localized_data.get('education', []):
        start_date = format_date(edu.get('startDate'), locale)
        end_date = format_date(edu.get('endDate'), locale)
        institution = escape_latex(edu.get('institution', ''))
        location = escape_latex(edu.get('location', ''))
        degree = escape_latex(build_degree_text(edu))

        edu_url_raw = edu.get('url', '')
        if edu_url_raw:
            edu_url = escape_latex(edu_url_raw)
            url_domain = escape_latex(
                edu.get('urlLabel')
                or edu_url_raw.replace('https://', '').replace('http://', '').rstrip('/')
            )
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
        r'(\% EDUCATION:START)(.*?)(\% EDUCATION:END)',
        lambda m: f'{m.group(1)}\n  \\resumeSubHeadingListStart\n{education_latex}  \\resumeSubHeadingListEnd\n  {m.group(3)}',
        "LaTeX education section",
    )

    # Update skills section
    skills_latex = "\\resumeItemListStart\n"

    for skill in localized_data.get('skills', []):
        skill_name = escape_latex(skill.get('name'))
        keywords = skill.get('keywords', [])

        if skill.get("_is_languages"):
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

    skills_latex += "  \\resumeItemListEnd"

    # Update the skills section in the LaTeX file
    latex_content = replace_section_or_raise(
        latex_content,
        r'(\% SKILLS:START)(.*?)(\% SKILLS:END)',
        lambda m: f'{m.group(1)}\n  {skills_latex}\n  {m.group(3)}',
        "LaTeX skills section",
    )

    for marker, value in (
        ("EXPERIENCE", strings["experience"]),
        ("EDUCATION", strings["education"]),
        ("SKILLS", strings["skills"]),
    ):
        latex_content = replace_marker(
            latex_content,
            f"% UI:{marker}:START",
            f"% UI:{marker}:END",
            f"\\section{{{escape_latex(value)}}}",
            f"LaTeX {marker.lower()} heading",
        )

    # Write updated content back to file
    with open(file_path, 'w') as file:
        file.write(latex_content)

def main():
    """Generate one web and PDF source version for every configured locale."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '../..'))

    yaml_path = os.path.join(repo_root, 'resume.yaml')
    html_path = os.path.join(repo_root, 'index.html')
    tex_path = os.path.join(repo_root, 'main.tex')

    data = load_yaml_data(yaml_path)

    with open(html_path, 'r') as file:
        html_template = file.read()
    with open(tex_path, 'r') as file:
        tex_template = file.read()

    generated_files = []
    for locale in get_locales(data):
        directory = locale_directory(data, locale)
        output_dir = repo_root if directory == "." else os.path.join(repo_root, directory)
        os.makedirs(output_dir, exist_ok=True)
        asset_prefix = "" if directory == "." else "../"
        localized_html_path = os.path.join(output_dir, "index.html")
        localized_tex_path = os.path.join(output_dir, "main.tex")
        update_html_file(data, localized_html_path, locale, asset_prefix, html_template)
        update_latex_file(data, localized_tex_path, locale, tex_template)
        generated_files.extend([localized_html_path, localized_tex_path])

    print(f"Updated HTML and LaTeX files successfully! Generated {len(generated_files)} localized resume files.")

if __name__ == "__main__":
    main()
