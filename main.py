import os
import json
import argparse
from typing import Dict
from datetime import datetime
from generator import generate_resume_json
from validator import validate_resume
from renderer import render_html
from exporter import export_html, export_pdf

INPUT_DIR = "input"
TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"

# Available templates
TEMPLATES = {
    "harvard": "template_harvard.html",
    "enhancv": "template_enhancv.html.html",
    "resumeio": "template_resumeio.html"
}


def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise SystemExit(f"❌ Error: File '{path}' not found. Please create this file first.")
    except Exception as e:
        raise SystemExit(f"❌ Error reading file '{path}': {e}")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters."""
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    # Limit length
    if len(filename) > 50:
        filename = filename[:50]
    return filename


def create_resume_folder(job_description: str, template: str, resume_json: Dict) -> str:
    """Create organized folder for the resume."""
    
    # Create main resumes directory
    resumes_dir = "resumes"
    try:
        os.makedirs(resumes_dir, exist_ok=True)
    except PermissionError:
        raise SystemExit("❌ Error: Permission denied creating 'resumes' directory.")
    except Exception as e:
        raise SystemExit(f"❌ Error creating directory: {e}")
    
    # Generate a unique identifier
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Try to extract job title from job description
    job_title = "Manual_Job_Application"
    if job_description:
        # Look for common job title patterns
        import re
        title_patterns = [
            r'position[:\s]+([^\n]+)',
            r'role[:\s]+([^\n]+)',
            r'job[:\s]+([^\n]+)',
            r'seeking[:\s]+([^\n]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                job_title = sanitize_filename(match.group(1).strip())
                break
    
    # Create folder name: JobTitle_Template_Timestamp
    folder_name = f"{job_title}_{template}_{batch_id}"
    folder_path = os.path.join(resumes_dir, folder_name)
    
    try:
        os.makedirs(folder_path, exist_ok=True)
    except PermissionError:
        raise SystemExit(f"❌ Error: Permission denied creating folder '{folder_path}'.")
    except Exception as e:
        raise SystemExit(f"❌ Error creating folder: {e}")
    
    return folder_path


def save_resume_files(folder_path: str, html_content: str, template: str, resume_json: Dict, job_description: str) -> None:
    """Save all resume-related files in the organized folder."""
    
    try:
        # Save resume files
        html_path = os.path.join(folder_path, f"resume_{template}.html")
        pdf_path = os.path.join(folder_path, f"resume_{template}.pdf")
        
        export_html(html_content, html_path)
        export_pdf(html_content, pdf_path)
        
        # Save resume data JSON
        resume_data_path = os.path.join(folder_path, "resume_data.json")
        with open(resume_data_path, 'w', encoding='utf-8') as f:
            json.dump(resume_json, f, indent=2, ensure_ascii=False)
        
        # Save job description
        job_desc_path = os.path.join(folder_path, "job_description.txt")
        with open(job_desc_path, 'w', encoding='utf-8') as f:
            f.write(job_description)
        
        # Save generation info
        info_path = os.path.join(folder_path, "generation_info.txt")
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(f"Template: {template}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Method: Traditional (manual job description)\n")
        
        print(f"Resume saved to: {folder_path}")
        print(f"HTML: {html_path}")
        print(f"PDF: {pdf_path}")
        
    except PermissionError:
        raise SystemExit(f"❌ Error: Permission denied writing to folder '{folder_path}'.")
    except Exception as e:
        raise SystemExit(f"❌ Error saving files: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate resume from templates')
    parser.add_argument('--template', choices=list(TEMPLATES.keys()), 
                       default='harvard', help='Template to use (default: harvard)')
    args = parser.parse_args()
    
    template_name = TEMPLATES[args.template]
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    
    # Validate template file exists
    if not os.path.exists(template_path):
        raise SystemExit(f"❌ Error: Template file '{template_path}' not found.")
    
    job_desc_path = os.path.join(INPUT_DIR, "job_description.txt")
    user_details_path = os.path.join(INPUT_DIR, "user_details.txt")

    job_description = read_file(job_desc_path)
    user_details = read_file(user_details_path)

    # Validate input data is not empty
    if not job_description.strip():
        raise SystemExit("❌ Error: Job description file is empty. Please add job details.")
    
    if not user_details.strip():
        raise SystemExit("❌ Error: User details file is empty. Please add your information.")

    MAX_ATTEMPTS = 2  # Strict limit to prevent token waste
    attempts = 0
    errors = None
    resume_json = {}
    validation_errors = ["initial"]

    while validation_errors and attempts < MAX_ATTEMPTS:
        resume_json = generate_resume_json(job_description, user_details, errors)
        
        # Validate the LLM-generated data (no cleaning/modification)
        validation_errors = validate_resume(resume_json)
        if validation_errors:
            errors = "\n".join(validation_errors)
            attempts += 1
            print(f"⚠️  Validation attempt {attempts}/{MAX_ATTEMPTS}: {len(validation_errors)} errors")

    if validation_errors:
        print(f"❌ Failed to generate valid resume JSON after {MAX_ATTEMPTS} attempts")
        print("📋 Final validation errors:")
        for error in validation_errors:
            print(f"  - {error}")
        print("💡 Consider manually reviewing your user details or job description")
        raise SystemExit("Resume generation failed - please check your input data")

    html_content = render_html(resume_json, template_path)
    
    # Create organized folder and save files
    folder_path = create_resume_folder(job_description, args.template, resume_json)
    save_resume_files(folder_path, html_content, args.template, resume_json, job_description)
    
    print(f"Resume generated successfully using {args.template} template!")


if __name__ == "__main__":
    main()
