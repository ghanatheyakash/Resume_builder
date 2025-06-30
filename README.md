# Resume Builder

This project demonstrates a simple pipeline that generates a resume from plain text files. The process includes:

1. Reading a job description and user details.
2. Generating structured JSON data.
3. Validating the JSON with `jsonschema`.
4. Rendering an HTML resume with Jinja2.
5. Exporting the resume to HTML and PDF using WeasyPrint.

Run `python3 main.py` to execute the pipeline. Generated files are placed in the `output/` directory.
