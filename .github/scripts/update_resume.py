#!/usr/bin/env python3
import yaml
import re
import os
from datetime import datetime

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
        except:
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
        start_date = format_date(job.get('startDate'))
        end_date = format_date(job.get('endDate'))

        highlights_html = ""
        for highlight in job.get('highlights', []):
            highlights_html += f'<li>{highlight}</li>\n'

        work_html += f'''
        <div class="lin-glass lin-dual-border p-6">
            <h3 class="text-xl font-bold text-white">{job.get('name', '')}</h3>
            <p class="text-white">{job.get('position', '')}</p>
            <p class="lin-text-secondary mb-2">{job.get('location', '')} | {start_date} - {end_date}</p>
            <ul class="list-disc list-inside text-white space-y-1">
                <li>{job.get('summary', '')}</li>
                {highlights_html}
            </ul>
        </div>
        '''

    # Update education section
    education_html = ""
    for edu in data.get('education', []):
        start_date = format_date(edu.get('startDate'))
        end_date = format_date(edu.get('endDate'))

        courses_html = ""
        for course in edu.get('courses', []):
            courses_html += f'<li>{course}</li>\n'

        degree_type = "Master of Business Administration (MBA)" if edu.get('studyType') == "Master" else f"Bachelor of Science in {edu.get('area')} (BSc)"

        education_html += f'''
        <div class="lin-glass lin-dual-border p-6">
            <h3 class="text-xl font-bold text-white">{edu.get('institution', '')}</h3>
            <p class="text-white">{degree_type}</p>
            <p class="lin-text-secondary mb-2">{edu.get('location', '')} | {start_date} - {end_date}</p>
            <ul class="list-disc list-inside text-white space-y-1">
                {courses_html}
            </ul>
        </div>
        '''

    # Update skills section
    skills_html = "<ul class=\"list-disc list-inside text-white space-y-2\">\n"
    for skill in data.get('skills', []):
        if skill.get('name') == "Languages":
            skills_html += f'<li>Languages: {", ".join(skill.get("keywords", []))}</li>\n'
        else:
            skills_html += f'<li>Skills and Tools: {", ".join(skill.get("keywords", []))}</li>\n'
    skills_html += "</ul>"

    # Replace content in HTML using regex patterns
    # Experience section
    html_content = re.sub(
        r'(<section class="mt-10 w-full">.*?<h2.*?>Experience.*?</h2>.*?<div class="space-y-6">)(.*?)(<\/div>\s*<\/section>)',
        f'\\1\n{work_html}\n\\3',
        html_content,
        flags=re.DOTALL
    )

    # Education section
    html_content = re.sub(
        r'(<section class="mt-10 w-full">.*?<h2.*?>Education.*?</h2>.*?<div class="space-y-6">)(.*?)(<\/div>\s*<\/section>)',
        f'\\1\n{education_html}\n\\3',
        html_content,
        flags=re.DOTALL
    )

    # Skills section
    html_content = re.sub(
        r'(<section class="mt-10 w-full">.*?<h2.*?>Skills.*?</h2>.*?<div class="lin-glass lin-dual-border p-6">)(.*?)(<\/div>\s*<\/section>)',
        f'\\1\n{skills_html}\n\\3',
        html_content,
        flags=re.DOTALL
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
    name = basics.get('name', '')
    label = basics.get('label', '')
    email = basics.get('email', '')
    github_profile = next((p for p in basics.get('profiles', []) if p.get('network') == 'GitHub'), {})
    linkedin_profile = next((p for p in basics.get('profiles', []) if p.get('network') == 'LinkedIn'), {})
    github_url = github_profile.get('url', '')
    github_username = github_profile.get('username', '')
    linkedin_url = linkedin_profile.get('url', '')
    linkedin_username = linkedin_profile.get('username', '')

    # Update header section with proper escaping for LaTeX
    header_latex = f'''\\\\textbf{{\\\\LARGE {name}}}
& Email: & \\\\href{{mailto:{email}}}{{{email}}} \\\\\\\\
{{\\\\large {label}}}
& Github: & \\\\href{{{github_url}}}{{github.com/{github_username}}} \\\\\\\\
& LinkedIn: & \\\\href{{{linkedin_url}}}{{linkedin.com/in/{linkedin_username}}} \\\\\\\\'''

    # Update the header in the LaTeX file with proper escaping
    latex_content = re.sub(
        r'\\begin\{tabular\*\}\{\\textwidth\}.*?\\end\{tabular\*\}',
        f'''\\\\begin{{tabular*}}{{\\\\textwidth}}
    {{
    l@{{\\\\extracolsep{{\\\\fill}}}}l
    @{{\\\\extracolsep{{6pt}}}}r
    l@{{\\\\extracolsep{{\\\\fill}}}}l
    @{{\\\\extracolsep{{6pt}}}}r
    @{{\\\\extracolsep{{6pt}}}}r
    @{{\\\\extracolsep{{6pt}}}}r
    }}

{header_latex}

\\\\end{{tabular*}}''',
        latex_content,
        flags=re.DOTALL
    )

    # Update experience section
    work_latex = ""
    for job in data.get('work', []):
        start_date = format_date(job.get('startDate'))
        end_date = format_date(job.get('endDate'))
        job_name = job.get('name', '')
        job_url = job.get('url', '')
        url_domain = job_url.replace('https://', '').replace('http://', '')
        position = job.get('position', '')
        location = job.get('location', '')
        summary = job.get('summary', '')

        work_latex += f'''  \\\\resumeSubheading
      {{{job_name} \\\\href{{{job_url}}}{{{url_domain}}}}}{{{location}}}
      {{{position}}}{{{start_date} - {end_date}}}
      \\\\resumeItemListStart
        \\\\resumeItemNoTitle
            {{{summary}}}
'''

        for highlight in job.get('highlights', []):
            work_latex += f'''        \\\\resumeItemNoTitle
            {{{highlight}}}
'''

        work_latex += '''      \\\\resumeItemListEnd
'''

    # Update the experience section in the LaTeX file
    latex_content = re.sub(
        r'\\section\{Experience\}.*?\\resumeSubHeadingListStart(.*?)\\resumeSubHeadingListEnd',
        f'\\\\section{{Experience}}\n\n\\\\resumeSubHeadingListStart\n{work_latex}\\\\resumeSubHeadingListEnd',
        latex_content,
        flags=re.DOTALL
    )

    # Update education section
    education_latex = ""
    for edu in data.get('education', []):
        start_date = format_date(edu.get('startDate'))
        end_date = format_date(edu.get('endDate'))
        institution = edu.get('institution', '')
        location = edu.get('location', '')
        study_type = edu.get('studyType', '')
        area = edu.get('area', '')

        # Determine degree type based on study type
        if study_type == "Master":
            degree = f"Master of {area} (MBA)"
        else:
            degree = f"Bachelor of Science in {area} (BSc)"

        education_latex += f'''    \\\\resumeSubheading
      {{{institution}}}{{{location}}}
      {{{degree} }}{{{start_date} -- {end_date}}}

      \\\\resumeItemListStart
'''

        for course in edu.get('courses', []):
            education_latex += f'''        \\\\resumeSubItemNoBullet
          {{{course}}}
'''

        education_latex += '''      \\\\resumeItemListEnd

'''

    # Update the education section in the LaTeX file
    latex_content = re.sub(
        r'\\section\{Education\}.*?\\resumeSubHeadingListStart(.*?)\\resumeSubHeadingListEnd',
        f'\\\\section{{Education}}\n  \\\\resumeSubHeadingListStart\n{education_latex}  \\\\resumeSubHeadingListEnd',
        latex_content,
        flags=re.DOTALL
    )

    # Update skills section
    skills_latex = " \\\\resumeItemListStart\n"

    for skill in data.get('skills', []):
        skill_name = skill.get('name')
        keywords = skill.get('keywords', [])

        if skill_name == "Languages":
            skills_latex += f'''    \\\\resumeItem{{{skill_name}}}{{}}\\\\vspace{{-3pt}}{{
        \\\\resumeItemListStart
'''
            for language in keywords:
                parts = language.split("(")
                if len(parts) > 1:
                    lang_name = parts[0].strip()
                    lang_level = f"({parts[1]}"
                    skills_latex += f'''            \\\\resumeItem{{{lang_name}}}{{{lang_level}}}
'''
                else:
                    skills_latex += f'''            \\\\resumeItem{{{language}}}{{}}
'''

            skills_latex += '''        \\\\resumeItemListEnd
    }
'''
        else:
            skills_latex += f'''    \\\\resumeItem{{{skill_name}}}{{}}\\\\vspace{{-3pt}}{{
        \\\\resumeItemListStart
            \\\\resumeItemNoTitle
            {{{' | '.join(keywords)}}}
        \\\\resumeItemListEnd
    }}
'''

    skills_latex += " \\\\resumeItemListEnd\n"

    # Update the skills section in the LaTeX file
    latex_content = re.sub(
        r'\\section\{Skills \\& Competencies\}.*?\\resumeItemListStart(.*?)\\resumeItemListEnd',
        f'\\\\section{{Skills \\\\& Competencies}}\n{skills_latex}',
        latex_content,
        flags=re.DOTALL
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