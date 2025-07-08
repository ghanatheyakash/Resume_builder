import json
import os
import argparse
from jinja2 import Template

def boldify(text):
    import re
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def boldify_all(data):
    if isinstance(data, dict):
        return {k: boldify_all(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [boldify_all(item) for item in data]
    elif isinstance(data, str):
        return boldify(data)
    else:
        return data

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = '_'.join(filename.split())
    return filename

def extract_role_and_company(jd_file='job_discription.txt'):
    import re
    try:
        with open(jd_file, 'r', encoding='utf-8') as f:
            content = f.read()
        role_patterns = [
            r'as a ([^,\n]+) at ([^,\n]+)',
            r'([^,\n]+) at ([^,\n]+)',
            r'position: ([^,\n]+)',
            r'role: ([^,\n]+)',
            r'job title: ([^,\n]+)',
            r'we are looking for a ([^,\n]+)',
            r'seeking a ([^,\n]+)',
        ]
        role = None
        company = None
        for pattern in role_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:
                    role = matches[0][0].strip()
                    company = matches[0][1].strip()
                    break
                elif len(matches[0]) == 1:
                    role = matches[0][0].strip()
                    break
        if role and not company:
            company_patterns = [
                r'at ([A-Z][a-zA-Z\s&]+)',
                r'with ([A-Z][a-zA-Z\s&]+)',
                r'([A-Z][a-zA-Z\s&]+) is looking',
                r'([A-Z][a-zA-Z\s&]+) seeks',
            ]
            for pattern in company_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    company = matches[0].strip()
                    break
        if role:
            role = re.sub(r'^(a|an|the)\s+', '', role, flags=re.IGNORECASE).strip()
        if company:
            company = re.sub(r'\s+(inc|corp|llc|ltd|company|co)\.?$', '', company, flags=re.IGNORECASE).strip()
        return role, company
    except Exception:
        return None, None

def load_resume_data(path='optimized_resume.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    header = data.get('header', {})
    data['full_name'] = header.get('full_name', '')
    data['title'] = header.get('title', '')
    data['email'] = header.get('email', '')
    data['phone'] = header.get('phone', '')
    data['linkedin'] = header.get('linkedin', '')
    data['github'] = header.get('github', '')
    data['location'] = header.get('location', '')
    data['summary'] = data.get('summary', '')
    data = boldify_all(data)
    if not isinstance(data, dict):
        raise ValueError('Resume data must be a dict')
    return dict(data)

TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ full_name }} – {{ title }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: 'Times New Roman', Times, serif; background: #fff; color: #222; margin: 0; padding: 0; }
    .container { max-width: 800px; margin: 0 auto; padding: 20px 20px 15px 20px; background: #fff; }
    .header { text-align: center; margin-bottom: 18px; }
    .name { font-size: 2.1em; font-weight: bold; letter-spacing: 2px; }
    .location { font-size: 1.1em; margin-top: 2px; }
    .contact { font-size: 1em; margin-top: 2px; }
    .contact a { color: #222; text-decoration: underline; }
    hr { border: none; border-top: 1.5px solid #222; margin: 18px 0 10px 0; }
    .section-title { font-size: 1.1em; font-weight: bold; letter-spacing: 1px; margin-bottom: 2px; margin-top: 18px; }
    .section-title-line { display: flex; align-items: center; margin-bottom: 6px; }
    .section-title-line span { margin-right: 10px; }
    .section-title-line hr { flex: 1; border-top: 1.2px solid #222; margin: 0; }
    .summary, .objective { font-size: 1.05em; margin-bottom: 10px; }
    .skills { margin-bottom: 10px; }
    .skills-row { margin-bottom: 2px; }
    .skills-category { font-weight: bold; margin-right: 6px; display: inline-block; min-width: 90px; vertical-align: top; font-size: 0.98em; }
    .skills-list { display: inline; }
    .skill-chip {
      display: inline-block;
      background: #e3eafc;
      color: #222;
      border-radius: 10px;
      padding: 1px 7px;
      margin: 1px 3px 1px 0;
      font-size: 0.97em;
      border: 1px solid #b6c6e6;
      vertical-align: middle;
    }
    .exp-block { margin-bottom: 13px; }
    .exp-header { display: flex; justify-content: space-between; align-items: baseline; }
    .exp-title { font-weight: bold; font-size: 1.05em; }
    .exp-company { font-style: italic; font-size: 1em; }
    .exp-location { font-size: 0.98em; color: #444; }
    .exp-dates { font-size: 0.98em; color: #444; }
    .exp-bullets { margin: 0 0 0 18px; }
    .edu-block { margin-bottom: 7px; }
    .edu-degree { font-weight: bold; }
    .edu-university { font-style: italic; }
    .edu-graduation { color: #444; }
    ul { margin-top: 2px; margin-bottom: 2px; }
    li { margin-bottom: 2px; }
    @media print {
      body, .container { background: #fff !important; color: #000 !important; }
      .container { box-shadow: none !important; }
      a { color: #000 !important; text-decoration: underline; }
      hr { border-top: 1.2px solid #000 !important; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="name">{{ full_name|upper }}</div>
      <div class="location">{{ location }}</div>
      <div class="contact">
        {{ phone }} | <a href="mailto:{{ email }}">{{ email }}</a> |
        <a href="{{ linkedin }}">LinkedIn/{{ linkedin.split('/')[-1] }}</a> |
        <a href="{{ github }}">Github/{{ github.split('/')[-1] }}</a>
      </div>
    </div>
    <div class="section-title-line"><span class="section-title">Career Objective</span><hr></div>
    <div class="objective">{{ summary|safe }}</div>
    <div class="section-title-line"><span class="section-title">Technical (IT) Skills</span><hr></div>
    <div class="skills">
      {% for category, items in skills.items() %}
        <div class="skills-row">
          <span class="skills-category">{{ category|capitalize }}:</span>
          <span class="skills-list">
            {% for skill in items %}<span class="skill-chip">{{ skill|safe }}</span>{% endfor %}
          </span>
        </div>
      {% endfor %}
    </div>
    <div class="section-title-line"><span class="section-title">Work Experience</span><hr></div>
    {% for exp in experience %}
    <div class="exp-block">
      <div class="exp-header">
        <span class="exp-title">{{ exp.title|safe }}</span>
        <span class="exp-dates">{{ exp.dates|safe }}</span>
      </div>
      <div class="exp-header">
        <span class="exp-company">{{ exp.company|safe }}</span>
        <span class="exp-location">{{ exp.location|safe }}</span>
      </div>
      <ul class="exp-bullets">
        {% for bullet in exp.bullets %}
        <li>{{ bullet|safe }}</li>
        {% endfor %}
      </ul>
    </div>
    {% endfor %}
    <div class="section-title-line"><span class="section-title">Education</span><hr></div>
    {% for edu in education %}
    <div class="edu-block">
      <span class="edu-degree">{{ edu.degree|safe }}</span>,
      <span class="edu-university">{{ edu.university|safe }}</span>
      (<span class="edu-graduation">{{ edu.graduation|safe }}</span>)
    </div>
    {% endfor %}
    {% if certifications %}
    <div class="section-title-line"><span class="section-title">Certifications</span><hr></div>
    <ul>
      {% for cert in certifications %}
      <li>{{ cert.name|safe }} ({{ cert.issuer|safe }}, {{ cert.year|safe }})</li>
      {% endfor %}
    </ul>
    {% endif %}
  </div>
</body>
</html>
'''

def main():
    parser = argparse.ArgumentParser(description='Generate HTML resume with custom naming')
    parser.add_argument('--role', '-r', help='Job role/position you are applying for (overrides JD extraction)')
    parser.add_argument('--company', '-c', help='Company name you are applying to (overrides JD extraction)')
    parser.add_argument('--output-dir', '-o', default='resumes', help='Output directory for generated files')
    parser.add_argument('--resume-data', '-d', default='optimized_resume.json', help='Path to resume JSON data')
    parser.add_argument('--job-description', '-j', default='job_discription.txt', help='Path to job description file')
    args = parser.parse_args()

    # Prefer role/company from JSON, then CLI, then JD extraction
    resume = load_resume_data(args.resume_data)
    role_from_json = resume.get('role')
    company_from_json = resume.get('company')
    role = role_from_json or args.role
    company = company_from_json or args.company
    if not role or not company:
        extracted_role, extracted_company = extract_role_and_company(args.job_description)
        if not role and extracted_role:
            role = extracted_role
        if not company and extracted_company:
            company = extracted_company
    if role and company:
        role_clean = sanitize_filename(role)
        company_clean = sanitize_filename(company)
        folder_name = f"{role_clean}_{company_clean}"
        base_filename = "Resume"
    elif role:
        role_clean = sanitize_filename(role)
        folder_name = f"{role_clean}"
        base_filename = "Resume"
    elif company:
        company_clean = sanitize_filename(company)
        folder_name = f"{company_clean}"
        base_filename = "Resume"
    else:
        folder_name = "Generic"
        base_filename = "Resume"
    full_output_dir = os.path.join(args.output_dir, folder_name)
    os.makedirs(full_output_dir, exist_ok=True)
    html_file = os.path.join(full_output_dir, f"{base_filename}.html")
    pdf_file = os.path.join(full_output_dir, f"{base_filename}.pdf")
    jd_dest = os.path.join(full_output_dir, "job_description.txt")
    try:
        import shutil
        shutil.copy2(args.job_description, jd_dest)
    except Exception:
        pass
    template = Template(TEMPLATE)
    html = template.render(**resume)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    try:
        from utils.pdf_converter import convert_html_to_pdf
        success = convert_html_to_pdf(html_file, pdf_file)
        if not success:
            print('PDF generation failed, but HTML file was created successfully')
    except ImportError:
        print('PDF converter not available. HTML file generated successfully.')
        print('To generate PDF, install the required dependencies and run:')
        print(f'python convert_to_pdf.py --input {html_file} --output {pdf_file}')

if __name__ == '__main__':
    main() 