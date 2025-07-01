from typing import List, Dict
from jsonschema import validate, ValidationError

resume_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string"},
        "phone": {"type": ["string", "null"]},
        "linkedin": {"type": ["string", "null"]},
        "github": {"type": ["string", "null"]},
        "website": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "job_title": {"type": ["string", "null"]},
        "summary": {"type": ["string", "null"]},
        "skills": {"type": "array", "items": {"type": "string"}},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string"},
                    "company": {"type": "string"},
                    "dates": {"type": ["string", "null"]},
                    "responsibilities": {"type": ["array", "null"], "items": {"type": "string"}}
                },
                "required": ["role", "company"]
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": "string"},
                    "school": {"type": "string"},
                    "dates": {"type": ["string", "null"]}
                },
                "required": ["degree", "school"]
            }
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "tech": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]}
                },
                "required": ["name"]
            }
        },
        "certifications": {"type": "array", "items": {"type": "string"}},
        "job_description": {"type": "string"}
    },
    "required": ["name", "email"],
}


def validate_resume(resume_json: Dict) -> List[str]:
    """Validate resume JSON against the schema. Returns a list of error messages."""
    errors: List[str] = []
    
    # Validate input is a dictionary
    if not isinstance(resume_json, dict):
        errors.append("Resume data must be a dictionary/object")
        return errors
    
    try:
        validate(instance=resume_json, schema=resume_schema)
    except ValidationError as e:
        errors.append(f"Validation error: {str(e.message)}")
    except Exception as e:
        errors.append(f"Schema validation failed: {str(e)}")
    
    # Additional custom validations
    custom_errors = perform_custom_validations(resume_json)
    errors.extend(custom_errors)
    
    return errors


def perform_custom_validations(resume_json: Dict) -> List[str]:
    """Perform additional custom validations beyond JSON schema."""
    errors = []
    
    # Check if name is not empty
    name = resume_json.get("name", "")
    if not isinstance(name, str) or not name.strip():
        errors.append("Name cannot be empty")
    
    # Check if email is valid format (but allow empty)
    email = resume_json.get("email", "")
    if isinstance(email, str) and email and "@" not in email:
        errors.append("Email must contain '@' symbol")
    
    # Check if experience entries have valid structure
    experience = resume_json.get("experience", [])
    if not isinstance(experience, list):
        errors.append("Experience must be a list")
    else:
        for i, exp in enumerate(experience):
            if not isinstance(exp, dict):
                errors.append(f"Experience entry {i+1} must be an object")
                continue
            
            # Only require role and company
            if not exp.get("role"):
                errors.append(f"Experience entry {i+1} must have a role")
            
            if not exp.get("company"):
                errors.append(f"Experience entry {i+1} must have a company")
    
    # Check if education entries have valid structure
    education = resume_json.get("education", [])
    if not isinstance(education, list):
        errors.append("Education must be a list")
    else:
        for i, edu in enumerate(education):
            if not isinstance(edu, dict):
                errors.append(f"Education entry {i+1} must be an object")
                continue
            
            # Only require degree and school
            if not edu.get("degree"):
                errors.append(f"Education entry {i+1} must have a degree")
            
            if not edu.get("school"):
                errors.append(f"Education entry {i+1} must have a school")
    
    return errors
