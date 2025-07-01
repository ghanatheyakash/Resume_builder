import os
from typing import Dict
from jinja2 import Environment, FileSystemLoader


def render_html(resume_data: Dict, template_path: str) -> str:
    """Render resume HTML using the Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        autoescape=True
    )
    template = env.get_template(os.path.basename(template_path))
    # Pass resume data directly to template (not wrapped in 'resume' object)
    result = template.render(**resume_data)
    return str(result)
