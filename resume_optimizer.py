import json
import os
from typing import Dict, Any
import google.generativeai as genai

def setup_gemini(api_key: str):
    """Setup Gemini API with the provided API key."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    return model

def optimize_resume(resume_json: Dict[str, Any], job_description: str, model) -> Dict[str, Any]:
    """
    Optimize the resume based on the job description using Gemini 2.0 Flash model.
    """
    # Gemini prompt for optimized resume JSON
    prompt = f"""
    You are an expert resume generator for AI roles in the U.S. job market. Given a candidate profile and a job description, your task is to output a complete, properly structured resume in **valid JSON format only**. Do not include any commentary, explanations, or text outside of the JSON block.

    The output must follow the schema below and support LaTeX/Markdown rendering using **double asterisks (**) for bold text** to highlight key terms.

    ### OUTPUT FORMAT: JSON ONLY

    #### 0. `role`, `company`, and `job_description` (strings)
    - Top-level fields. Extracted from the job description if possible.
    - `job_description` must be the exact text provided as input.
    - Example: "role": "Data Scientist", "company": "Google", "job_description": "As a Data Scientist at Google..."

    #### 1. `header` (object)
    - `full_name`, `title`, `email`, `phone`, `linkedin`, `github`, `location`
    - Title should match job role (e.g., "**Senior Machine Learning Engineer**")
    - No photos, DOB, full addresses, or personal info

    #### 2. `summary` (string)
    - 80–120 words
    - Describe candidate's experience, skills, tools, and impact
    - Must include **bolded keywords** like tools, models, metrics (e.g., **NLP**, **Python**, **30% accuracy gain**)

    #### 3. `skills` (object)
    Subcategories:
    - `programming`: e.g., ["**Python**", "**SQL**"]
    - `ml_frameworks`: e.g., ["**TensorFlow**", "**PyTorch**"]
    - `nlp_tools`, `data_engineering`, `cloud_devops`, `version_control`, `soft_skills`
    - All entries must use `**` around keywords

    #### 4. `experience` (array)
    Each entry must include:
    - `title`, `company`, `location`, `dates`
    - `bullets`: 10–15 concise, results-driven bullet points
    - Each bullet should begin with a strong action verb and contain bolded tools or metrics (e.g., **deployed**, **SageMaker**, **45%**)

    Edge Cases:
    - If role was freelance/contract, label it clearly
    - If metrics aren't available, use qualitative outcomes

    #### 5. `projects` (array)
    Each project must have:
    - `title`, `tech_stack` (array of bolded tools), `description`, `impact`, `link` (if any)
    - 2–3 lines per project max, all tools/keywords bolded

    If no projects are provided, return an empty array.

    #### 6. `education` (array)
    Each entry includes:
    - `degree`, `university`, `graduation`
    - Bold `degree` and `university` values

    #### 7. `certifications` (array)
    Each entry includes:
    - `name`, `issuer`, `year`
    - Bold `name` and `issuer`

    If none provided, return empty array.

    #### 8. `publications` (array)
    Each entry includes:
    - `title`, `venue`, `year`, `link` (optional)
    - Bold `title`

    Optional: can be omitted or empty array if not applicable

    #### 9. `awards` (array)
    Each entry: 1-line description with **bolded title or achievement**
    - e.g., "**Winner**, Bolt Hackathon 2025 – Prominence AEO Analyzer"

    Optional: return empty array if not provided

    ### IMPORTANT RULES:

    ✅ Output must be valid, parsable JSON.  
    ✅ Use `**` around tools, job titles, impact metrics, and model names for bolding.  
    ✅ DO NOT return Markdown, LaTeX, prose, or any other format.  
    ✅ DO NOT wrap JSON in triple backticks (```) — return JSON only.  
    ✅ Each section must follow the structure and formatting rules precisely.  
    ✅ Always prefer measurable outcomes (%, $, time, users) when available.
    ✅ Ensure the generated resume achieves a high ATS match score by including every required keyword from the JD exactly as provided—do not omit or paraphrase any.

    ### INPUT DATA:

    Job Description:
    {job_description}

    Original Resume (JSON):
    {json.dumps(resume_json, indent=2)}

    Now return only the final JSON resume object, including top-level 'role', 'company', and 'job_description' fields.
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the response to extract JSON
        response_text = response.text.strip()
        
        # Try to find JSON in the response (in case model adds extra text)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            optimized_resume = json.loads(json_str)
            return optimized_resume
        else:
            # If no JSON found, return original resume
            print("Warning: Could not parse JSON from model response. Returning original resume.")
            return resume_json
            
    except Exception as e:
        print(f"Error optimizing resume: {e}")
        return resume_json

def main():
    """Main function to run the resume optimizer."""
    print("=== Resume Optimizer using Gemini 2.0 Flash ===")
    print()
    
    # Use the hardcoded API key
    api_key = "paste your api key here"
    print("Using provided API key...")
    
    try:
        # Setup Gemini model
        print("Setting up Gemini model...")
        model = setup_gemini(api_key)
        print("✓ Model setup complete!")
        
        # Load resume file
        resume_file = "resume.json"
        if not os.path.exists(resume_file):
            print(f"Error: {resume_file} not found!")
            return
        
        print(f"Loading resume from {resume_file}...")
        try:
            with open(resume_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"Error: {resume_file} is empty!")
                    return
                resume_json = json.loads(content)
            print("✓ Resume loaded successfully!")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {resume_file}: {e}")
            return
        except Exception as e:
            print(f"Error reading {resume_file}: {e}")
            return
        
        # Load job description file
        job_file = "job_discription.txt"
        if not os.path.exists(job_file):
            print(f"Error: {job_file} not found!")
            return
        
        print(f"Loading job description from {job_file}...")
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_description = f.read().strip()
                if not job_description:
                    print(f"Error: {job_file} is empty!")
                    return
            print("✓ Job description loaded successfully!")
        except Exception as e:
            print(f"Error reading {job_file}: {e}")
            return
        
        # Optimize resume
        print("\nOptimizing resume...")
        print("This may take a few moments...")
        optimized_resume = optimize_resume(resume_json, job_description, model)
        
        # Save optimized resume
        output_file = "optimized_resume.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_resume, f, indent=2)
        
        print(f"\n✓ Optimization complete!")
        print(f"✓ Optimized resume saved to: {output_file}")
        
        # Show summary of changes
        print("\n=== Summary ===")
        print(f"Original resume: {resume_file}")
        print(f"Job description: {job_file}")
        print(f"Optimized resume: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
