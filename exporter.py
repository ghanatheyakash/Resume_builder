from weasyprint import HTML


def export_html(html_content: str, output_path: str) -> None:
    """Save HTML content to a file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def export_pdf(html_content: str, output_path: str) -> None:
    """Export HTML content to PDF using WeasyPrint."""
    HTML(string=html_content).write_pdf(output_path)
