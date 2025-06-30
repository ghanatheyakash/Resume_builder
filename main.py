import os
import json
from generator import generate_resume_json
from validator import validate_resume
from renderer import render_html
from exporter import export_html, export_pdf

INPUT_DIR = "input"
TEMPLATE_PATH = os.path.join("templates", "resume.html.j2")
OUTPUT_DIR = "output"


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def main() -> None:
    job_desc_path = os.path.join(INPUT_DIR, "job_description.txt")
    user_details_path = os.path.join(INPUT_DIR, "user_details.txt")

    job_description = read_file(job_desc_path)
    user_details = read_file(user_details_path)

    attempts = 0
    errors = None
    resume_json = {}
    validation_errors = ["initial"]

    while validation_errors and attempts < 3:
        resume_json = generate_resume_json(job_description, user_details, errors)
        validation_errors = validate_resume(resume_json)
        if validation_errors:
            errors = "\n".join(validation_errors)
            attempts += 1

    if validation_errors:
        raise SystemExit(f"Failed to generate valid resume JSON after {attempts} attempts: {validation_errors}")

    html_content = render_html(resume_json, TEMPLATE_PATH)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html_path = os.path.join(OUTPUT_DIR, "resume.html")
    pdf_path = os.path.join(OUTPUT_DIR, "resume.pdf")

    export_html(html_content, html_path)
    export_pdf(html_content, pdf_path)
    print(f"Resume exported to {html_path} and {pdf_path}")


if __name__ == "__main__":
    main()
