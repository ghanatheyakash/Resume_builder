import streamlit as st
import os
import subprocess
import base64
import json
from glob import glob

# Display PDF in Streamlit
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Find the most recently modified PDF in resumes/ and subfolders
def get_latest_pdf(resumes_dir):
    pdf_files = [y for x in os.walk(resumes_dir) for y in glob(os.path.join(x[0], '*.pdf'))]
    if not pdf_files:
        return None
    return max(pdf_files, key=os.path.getmtime)

# Sanitize file names for download
def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = '_'.join(filename.split())
    return filename

def main():
    st.set_page_config(page_title="AI Resume Builder", layout="wide")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("## Job Description")
        job_description = st.text_area("Paste the job description here:", height=500)
        generate = st.button("Generate Resume", use_container_width=True)
    with col2:
        st.markdown("## Resume Preview")
        if generate and job_description:
            with st.spinner("Generating resume..."):
                # Overwrite the main job_discription.txt in the project root
                jd_path = os.path.abspath("job_discription.txt")
                with open(jd_path, "w", encoding="utf-8") as f:
                    f.write(job_description)
                resumes_dir = os.path.abspath("resumes")
                os.makedirs(resumes_dir, exist_ok=True)
                # Copy base resume.json to resumes dir (if needed by optimizer)
                base_resume = "resume.json"
                temp_resume = os.path.join(resumes_dir, "resume.json")
                if os.path.exists(base_resume):
                    with open(base_resume, "r", encoding="utf-8") as src, open(temp_resume, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                # Copy job_discription.txt to resumes dir
                temp_jd = os.path.join(resumes_dir, "job_discription.txt")
                with open(jd_path, "r", encoding="utf-8") as src, open(temp_jd, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
                # Run resume_optimizer.py in resumes dir
                subprocess.run([
                    "python", os.path.abspath("resume_optimizer.py")
                ], cwd=resumes_dir, check=True)
                # Run resume_to_html.py in resumes dir
                subprocess.run([
                    "python", os.path.abspath("resume_to_html.py"), "--resume-data", "optimized_resume.json", "--job-description", "job_discription.txt", "--output-dir", resumes_dir
                ], cwd=resumes_dir, check=True)
                # Find the latest generated PDF in resumes dir
                pdf_path = get_latest_pdf(resumes_dir)
                # Read role and company from optimized_resume.json for download filename
                opt_json_path = os.path.join(resumes_dir, "optimized_resume.json")
                role = company = None
                if os.path.exists(opt_json_path):
                    with open(opt_json_path, "r", encoding="utf-8") as f:
                        opt_json = json.load(f)
                        role = opt_json.get("role")
                        company = opt_json.get("company")
                if pdf_path and os.path.exists(pdf_path):
                    display_pdf(pdf_path)
                    if role and company:
                        file_name = f"Resume_{sanitize_filename(role)}_{sanitize_filename(company)}.pdf"
                    else:
                        file_name = os.path.basename(pdf_path)
                    st.download_button(
                        label="Download PDF",
                        data=open(pdf_path, "rb").read(),
                        file_name=file_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("PDF not generated. Please check your scripts.")
        else:
            st.info("Paste a job description and click Generate Resume to preview.")

if __name__ == "__main__":
    main() 