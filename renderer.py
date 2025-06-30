import os
from typing import Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_html(resume_data: Dict, template_path: str) -> str:
    """Render resume HTML using the Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(os.path.basename(template_path))
    return template.render(resume=resume_data)
