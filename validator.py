from typing import List, Dict
from jsonschema import validate, ValidationError

resume_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "skills": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "email", "skills"],
}


def validate_resume(resume_json: Dict) -> List[str]:
    """Validate resume JSON against the schema. Returns a list of error messages."""
    errors: List[str] = []
    try:
        validate(instance=resume_json, schema=resume_schema)
    except ValidationError as e:
        errors.append(str(e.message))
    return errors
