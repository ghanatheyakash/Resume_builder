import json
from typing import Optional, Dict, List

# In a real implementation, this function would call an LLM service such as OpenAI
# to generate structured resume JSON from the user's details and job description.
# Here we provide a simple deterministic implementation that parses the user
# details text and returns a JSON structure.

def generate_resume_json(job_description: str, user_details: str, errors: Optional[str] = None) -> Dict:
    """Generate resume JSON from the provided texts."""
    data = {
        "name": None,
        "email": None,
        "skills": []
    }
    for line in user_details.splitlines():
        if line.lower().startswith("name:"):
            data["name"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("email:"):
            data["email"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("skills:"):
            skills = line.split(":", 1)[1].split(",")
            data["skills"] = [s.strip() for s in skills if s.strip()]
    # Attach job description for context (not validated)
    data["job_description"] = job_description
    if errors:
        data["errors"] = errors
    return data
