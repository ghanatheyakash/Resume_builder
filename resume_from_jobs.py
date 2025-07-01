#!/usr/bin/env python3
"""
Resume Generator from Job URLs
This script parses job URLs and generates targeted resumes based on the job descriptions.
Each job URL is processed individually through the complete pipeline.
"""

import os
import json
import argparse
from typing import List, Dict, Optional
from datetime import datetime
from job_parser import JobParser
from generator import generate_resume_json
from validator import validate_resume
from renderer import render_html
from exporter import export_html, export_pdf


def process_single_job(job_detail: Dict, user_details: str, template: str, resumes_dir: str) -> Optional[str]:
    """Process a single job through the complete pipeline: parse → generate → validate → render → export → store."""
    
    print(f"\n🔄 Processing: {job_detail.get('title', 'Unknown')} at {job_detail.get('company', 'Unknown')}")
    print("=" * 60)
    
    # Step 1: Create job description from single job
    job_description = create_job_description_from_single_job(job_detail)
    
    # Step 2: Generate resume JSON
    print("📝 Step 1: Generating resume JSON...")
    attempts = 0
    errors = None
    resume_json = {}
    validation_errors = ["initial"]
    
    MAX_ATTEMPTS = 2  # Strict limit to prevent token waste
    
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
        return None
    
    print("✅ Resume JSON generated successfully")
    
    # Step 3: Render HTML
    print("🎨 Step 2: Rendering HTML template...")
    templates = {
        "harvard": "template_harvard.html",
        "enhancv": "template_enhancv.html.html",
        "resumeio": "template_resumeio.html"
    }
    
    template_name = templates.get(template, templates["harvard"])
    template_path = os.path.join("templates", template_name)
    
    html_content = render_html(resume_json, template_path)
    print("✅ HTML rendered successfully")
    
    # Step 4: Create organized folder and save files
    print("📁 Step 3: Creating organized folder structure...")
    folder_path = create_job_specific_folder(job_detail, template, resumes_dir)
    
    # Step 5: Export to HTML and PDF
    print("📄 Step 4: Exporting to HTML and PDF...")
    html_path = os.path.join(folder_path, f"resume_{template}.html")
    pdf_path = os.path.join(folder_path, f"resume_{template}.pdf")
    
    export_html(html_content, html_path)
    export_pdf(html_content, pdf_path)
    print("✅ Files exported successfully")
    
    # Step 6: Save additional files
    print("💾 Step 5: Saving analysis and metadata...")
    save_job_specific_files(folder_path, job_detail, resume_json, job_description)
    
    print(f"✅ Complete! Resume saved to: {folder_path}")
    return folder_path


def create_job_description_from_single_job(job_detail: Dict) -> str:
    """Create a job description from a single parsed job."""
    description_parts = []
    
    description_parts.append(f"JOB DESCRIPTION: {job_detail.get('title', 'Unknown Position')}")
    description_parts.append(f"COMPANY: {job_detail.get('company', 'Unknown Company')}")
    description_parts.append(f"LOCATION: {job_detail.get('location', 'Unknown Location')}")
    description_parts.append(f"EXPERIENCE LEVEL: {job_detail.get('experience_level', 'Not specified')}")
    description_parts.append(f"JOB TYPE: {job_detail.get('job_type', 'Not specified')}")
    
    if job_detail.get('salary_range') and job_detail.get('salary_range') != "Not specified":
        description_parts.append(f"SALARY: {job_detail.get('salary_range')}")
    
    description_parts.append("\nREQUIRED SKILLS:")
    for skill in job_detail.get('skills', []):
        description_parts.append(f"• {skill}")
    
    description_parts.append("\nJOB REQUIREMENTS:")
    for req in job_detail.get('requirements', []):
        description_parts.append(f"• {req}")
    
    description_parts.append("\nFULL JOB DESCRIPTION:")
    description_parts.append(job_detail.get('description', 'No description available'))
    
    return "\n".join(description_parts)


def create_job_specific_folder(job_detail: Dict, template: str, resumes_dir: str) -> str:
    """Create a specific folder for a single job resume."""
    
    # Create main resumes directory
    os.makedirs(resumes_dir, exist_ok=True)
    
    # Generate a unique identifier
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create folder name: Role_Company_Timestamp
    role_name = sanitize_filename(job_detail.get('title', 'Unknown_Role'))
    company_name = sanitize_filename(job_detail.get('company', 'Unknown_Company'))
    
    folder_name = f"{role_name}_{company_name}_{batch_id}"
    folder_path = os.path.join(resumes_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_path


def save_job_specific_files(folder_path: str, job_detail: Dict, resume_json: Dict, job_description: str) -> None:
    """Save job-specific files in the resume folder."""
    
    # Save job details JSON
    job_details_path = os.path.join(folder_path, "job_details.json")
    with open(job_details_path, 'w', encoding='utf-8') as f:
        json.dump([job_detail], f, indent=2, ensure_ascii=False)
    
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
        f.write(f"Job Title: {job_detail.get('title', 'Unknown')}\n")
        f.write(f"Company: {job_detail.get('company', 'Unknown')}\n")
        f.write(f"Location: {job_detail.get('location', 'Unknown')}\n")
        f.write(f"Experience Level: {job_detail.get('experience_level', 'Not specified')}\n")
        f.write(f"Job Type: {job_detail.get('job_type', 'Not specified')}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Method: Individual Job URL Processing\n")
    
    # Generate and save analysis report
    report = generate_single_job_analysis_report(job_detail)
    report_path = os.path.join(folder_path, "job_analysis_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)


def generate_single_job_analysis_report(job_detail: Dict) -> str:
    """Generate analysis report for a single job."""
    report = []
    report.append("=" * 60)
    report.append("INDIVIDUAL JOB ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Job Title: {job_detail.get('title', 'Unknown')}")
    report.append(f"Company: {job_detail.get('company', 'Unknown')}")
    report.append(f"Location: {job_detail.get('location', 'Unknown')}")
    report.append(f"Experience Level: {job_detail.get('experience_level', 'Not specified')}")
    report.append(f"Job Type: {job_detail.get('job_type', 'Not specified')}")
    report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Skills analysis
    skills = job_detail.get('skills', [])
    if skills:
        report.append("REQUIRED SKILLS:")
        for skill in skills:
            report.append(f"• {skill}")
        report.append("")
    
    # Requirements analysis
    requirements = job_detail.get('requirements', [])
    if requirements:
        report.append("JOB REQUIREMENTS:")
        for req in requirements:
            report.append(f"• {req}")
        report.append("")
    
    # Salary information
    if job_detail.get('salary_range') and job_detail.get('salary_range') != "Not specified":
        report.append(f"SALARY RANGE: {job_detail.get('salary_range')}")
        report.append("")
    
    # Job description summary
    description = job_detail.get('description', '')
    if description:
        report.append("JOB DESCRIPTION SUMMARY:")
        # Take first 500 characters as summary
        summary = description[:500] + "..." if len(description) > 500 else description
        report.append(summary)
        report.append("")
    
    return "\n".join(report)


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


def main():
    """Main function for generating individual resumes from job URLs."""
    parser = argparse.ArgumentParser(description='Generate individual resumes from job URLs')
    parser.add_argument('--urls', nargs='+', help='Job URLs to parse')
    parser.add_argument('--urls-file', help='File containing job URLs (one per line)')
    parser.add_argument('--template', choices=['harvard', 'enhancv', 'resumeio'], 
                       default='harvard', help='Template to use (default: harvard)')
    parser.add_argument('--user-details', default='input/user_details.txt',
                       help='Path to user details file (default: input/user_details.txt)')
    parser.add_argument('--resumes-dir', default='resumes',
                       help='Directory to store resumes (default: resumes)')
    
    args = parser.parse_args()
    
    # Get URLs
    urls = []
    if args.urls:
        urls.extend(args.urls)
    
    if args.urls_file:
        try:
            with open(args.urls_file, 'r') as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                urls.extend(file_urls)
        except FileNotFoundError:
            print(f"Error: URLs file '{args.urls_file}' not found.")
            return
    
    if not urls:
        print("No URLs provided. Use --urls or --urls-file to specify job URLs.")
        return
    
    # Check if user details file exists
    if not os.path.exists(args.user_details):
        print(f"Error: User details file '{args.user_details}' not found.")
        print("Please create this file with your information (see README.md for format).")
        return
    
    # Read user details
    with open(args.user_details, 'r', encoding='utf-8') as f:
        user_details = f.read()
    
    # Parse all jobs first
    print("🔍 Parsing job URLs...")
    job_parser = JobParser()
    job_details = job_parser.parse_urls(urls)
    
    if not job_details:
        print("No jobs were successfully parsed. Exiting.")
        return
    
    print(f"✅ Successfully parsed {len(job_details)} job(s)")
    
    # Process each job individually through the complete pipeline
    successful_resumes = []
    failed_jobs = []
    
    for i, job_detail in enumerate(job_details, 1):
        print(f"\n🎯 Processing Job {i}/{len(job_details)}")
        print("=" * 60)
        
        # Convert JobDetails object to dictionary
        job_dict = {
            'url': job_detail.url,
            'title': job_detail.title,
            'company': job_detail.company,
            'location': job_detail.location,
            'description': job_detail.description,
            'requirements': job_detail.requirements,
            'skills': job_detail.skills,
            'experience_level': job_detail.experience_level,
            'job_type': job_detail.job_type,
            'salary_range': job_detail.salary_range,
            'parsed_at': job_detail.parsed_at
        }
        
        try:
            folder_path = process_single_job(job_dict, user_details, args.template, args.resumes_dir)
            if folder_path:
                successful_resumes.append({
                    'job': job_dict,
                    'folder': folder_path
                })
            else:
                failed_jobs.append(job_dict)
        except Exception as e:
            print(f"❌ Error processing job: {str(e)}")
            failed_jobs.append(job_dict)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {len(successful_resumes)} resume(s)")
    print(f"❌ Failed: {len(failed_jobs)} job(s)")
    
    if successful_resumes:
        print("\n📁 Generated Resume Folders:")
        for resume in successful_resumes:
            job = resume['job']
            folder = resume['folder']
            print(f"   • {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"     📂 {folder}")
    
    if failed_jobs:
        print("\n❌ Failed Jobs:")
        for job in failed_jobs:
            print(f"   • {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
    
    print(f"\n🎉 Process completed! Check the '{args.resumes_dir}' directory for your resumes.")


if __name__ == "__main__":
    main() 