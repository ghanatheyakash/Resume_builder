import json
import requests
from typing import Optional, Dict, List
import time

# Configuration constants
MAX_VALIDATION_ATTEMPTS = 2  # Prevent infinite loops and token waste
LLM_TIMEOUT = 30  # seconds
LLM_MAX_RETRIES = 2

# LLM Configuration for Llama 3 8B
LLM_CONFIG = {
    "base_url": "http://localhost:11434",  # Ollama default URL
    "model": "llama3:8b",  # User's installed model
    "temperature": 0.7,
    "max_tokens": 4000,
    "timeout": 120
}

def call_llama_api(prompt: str, max_retries: int = 2, timeout: int = 30) -> Optional[str]:
    """Call Llama 3 8B via Ollama API with timeout and retry logic."""
    
    url = f"{LLM_CONFIG['base_url']}/api/generate"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "model": LLM_CONFIG["model"],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": LLM_CONFIG["temperature"],
            "top_p": 0.9,
            "num_predict": LLM_CONFIG["max_tokens"]
        }
    }
    
    for attempt in range(max_retries + 1):
        try:
            print(f"🤖 Calling {LLM_CONFIG['model']} (attempt {attempt + 1}/{max_retries + 1})...")
            
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                print(f"⚠️  API call failed with status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout on attempt {attempt + 1} (after {timeout}s)")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error on attempt {attempt + 1}")
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
        
        if attempt < max_retries:
            print(f"🔄 Retrying in 2 seconds...")
            time.sleep(2)
    
    print("❌ All LLM API attempts failed")
    return None

def generate_resume_json(job_description: str, user_details: str, errors: Optional[str] = None) -> Dict:
    """Generate resume JSON using Llama 3.2 8B based on job description and user details."""
    
    print(f"🤖 Using {LLM_CONFIG['model']} to generate optimized resume...")
    
    # Test LLM connection first
    if not test_llama_connection():
        print("⚠️  LLM not available, falling back to text parsing...")
        return fallback_text_parsing(user_details, job_description, errors)
    
    # Create system prompt for Llama
    system_prompt = """You are an expert resume writer and career coach. Your task is to generate a professional resume in JSON format based on the user's details and a specific job description.

IMPORTANT RULES:
1. Always return valid JSON format
2. Optimize the resume content to match the job requirements
3. Highlight relevant skills and experiences
4. Use action verbs and quantifiable achievements
5. Ensure all dates and information are realistic
6. Focus on the most relevant experiences for the target job
7. Include specific skills mentioned in the job description
8. Make the summary compelling and job-specific

JSON STRUCTURE:
{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "linkedin": "linkedin profile",
    "github": "github profile",
    "website": "personal website",
    "location": "city, state",
    "job_title": "target job title",
    "summary": "professional summary tailored to the job",
    "skills": ["skill1", "skill2", "skill3"],
    "experience": [
        {
            "role": "Job Title",
            "company": "Company Name",
            "dates": "Start Date - End Date",
            "responsibilities": [
                "Achievement 1 with metrics",
                "Achievement 2 with metrics",
                "Achievement 3 with metrics"
            ]
        }
    ],
    "education": [
        {
            "degree": "Degree Name",
            "school": "University Name",
            "dates": "Graduation Year"
        }
    ],
    "projects": [
        {
            "name": "Project Name",
            "tech": "Technologies Used",
            "description": "Project description with impact"
        }
    ],
    "certifications": ["Certification 1", "Certification 2"]
}"""

    # Create the main prompt
    prompt = f"""Generate a professional resume in JSON format for the following job opportunity.

JOB DESCRIPTION:
{job_description}

USER DETAILS:
{user_details}

Generate a resume that:
1. Matches the job requirements and skills
2. Highlights relevant experience
3. Uses quantifiable achievements
4. Includes specific skills from the job description
5. Creates a compelling professional summary

Return ONLY the JSON object, no additional text or explanations."""

    # Call Llama API
    print(f"🔄 Generating resume with {LLM_CONFIG['model']}...")
    llm_response = call_llama_api(prompt)
    
    if not llm_response:
        print("⚠️  LLM generation failed, falling back to text parsing...")
        return fallback_text_parsing(user_details, job_description, errors)
    
    # Try to extract JSON from the response
    try:
        # Clean the response to extract JSON
        json_start = llm_response.find('{')
        json_end = llm_response.rfind('}') + 1
        
        if json_start != -1 and json_end != 0 and json_end > json_start:
            json_str = llm_response[json_start:json_end]
            
            # Validate JSON structure before parsing
            if not json_str.strip():
                print("⚠️  Empty JSON string found, falling back to text parsing...")
                return fallback_text_parsing(user_details, job_description, errors)
            
            resume_data = json.loads(json_str)
            
            # Ensure basic structure exists
            resume_data = ensure_basic_structure(resume_data)
            
            # Add job description for context
            resume_data["job_description"] = job_description
            if errors:
                resume_data["errors"] = errors
            
            print(f"✅ Resume generated successfully with {LLM_CONFIG['model']}!")
            return resume_data
            
        else:
            print("⚠️  No valid JSON found in LLM response, falling back to text parsing...")
            return fallback_text_parsing(user_details, job_description, errors)
            
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {e}")
        print("⚠️  Falling back to text parsing...")
        return fallback_text_parsing(user_details, job_description, errors)
    except Exception as e:
        print(f"⚠️  Error processing LLM response: {e}")
        print("⚠️  Falling back to text parsing...")
        return fallback_text_parsing(user_details, job_description, errors)

def ensure_basic_structure(resume_data: Dict) -> Dict:
    """Ensure basic structure exists for LLM output - ONLY add missing fields, never overwrite."""
    
    # Only add fields that are completely missing, preserve all LLM data
    required_fields = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "website": "",
        "location": "",
        "job_title": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": []
    }
    
    # Only add missing fields, never overwrite existing data
    for field, default_value in required_fields.items():
        if field not in resume_data:
            resume_data[field] = default_value
        # If field exists (even if None), leave it as LLM generated it
    
    return resume_data

def fallback_text_parsing(user_details: str, job_description: str, errors: Optional[str] = None) -> Dict:
    """Fallback to original text parsing method if LLM fails."""
    print("📝 Using fallback text parsing method...")
    
    data = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "website": None,
        "location": None,
        "job_title": None,
        "summary": None,
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": []
    }
    
    current_section = None
    
    for line in user_details.splitlines():
        line = line.strip()
        if not line:
            continue
            
        if line.lower().startswith("name:"):
            data["name"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("email:"):
            data["email"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("phone:"):
            data["phone"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("linkedin:"):
            data["linkedin"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("github:"):
            data["github"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("website:"):
            data["website"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("location:"):
            data["location"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("job title:"):
            data["job_title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("summary:"):
            data["summary"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("skills:"):
            skills = line.split(":", 1)[1].split(",")
            data["skills"] = [s.strip() for s in skills if s.strip()]
        elif line.lower().startswith("experience:"):
            current_section = "experience"
        elif line.lower().startswith("education:"):
            current_section = "education"
        elif line.lower().startswith("projects:"):
            current_section = "projects"
        elif line.lower().startswith("certifications:"):
            current_section = "certifications"
        elif line.startswith("-") and current_section == "experience":
            # Parse experience entry
            exp_parts = line[1:].strip().split("|")
            if len(exp_parts) >= 3:
                exp = {
                    "role": exp_parts[0].strip(),
                    "company": exp_parts[1].strip(),
                    "dates": exp_parts[2].strip(),
                    "responsibilities": []
                }
                data["experience"].append(exp)
        elif line.startswith("  *") and current_section == "experience" and data["experience"]:
            # Add responsibility to last experience entry
            data["experience"][-1]["responsibilities"].append(line[3:].strip())
        elif line.startswith("-") and current_section == "education":
            # Parse education entry
            edu_parts = line[1:].strip().split("|")
            if len(edu_parts) >= 3:
                edu = {
                    "degree": edu_parts[0].strip(),
                    "school": edu_parts[1].strip(),
                    "dates": edu_parts[2].strip()
                }
                data["education"].append(edu)
        elif line.startswith("-") and current_section == "projects":
            # Parse project entry
            project_parts = line[1:].strip().split("|")
            if len(project_parts) >= 3:
                project = {
                    "name": project_parts[0].strip(),
                    "tech": project_parts[1].strip(),
                    "description": project_parts[2].strip()
                }
                data["projects"].append(project)
        elif line.startswith("-") and current_section == "certifications":
            # Parse certification entry
            cert = line[1:].strip()
            data["certifications"].append(cert)
    
    # Attach job description for context (not validated)
    data["job_description"] = job_description
    if errors:
        data["errors"] = errors
    
    return data

def test_llama_connection() -> bool:
    """Test if Llama 3 8B is available and running."""
    try:
        url = f"{LLM_CONFIG['base_url']}/api/tags"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            for model in models:
                if LLM_CONFIG["model"] in model.get("name", ""):
                    print(f"✅ {LLM_CONFIG['model']} is available!")
                    return True
            print(f"⚠️  {LLM_CONFIG['model']} not found. Available models: {[m.get('name') for m in models]}")
            return False
        else:
            print("❌ Cannot connect to Ollama API")
            return False
    except Exception as e:
        print(f"❌ Error testing Llama connection: {e}")
        return False
