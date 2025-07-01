# 🤖 AI-Powered Resume Builder

An intelligent resume generator that uses Llama 3 8B to create targeted resumes based on job descriptions. The system processes job URLs, extracts requirements, and generates optimized resumes with multiple template options.

## ✨ Features

- **🤖 AI-Powered Generation**: Uses Llama 3 8B via Ollama for intelligent resume creation
- **🎯 Job-Specific Targeting**: Parses job URLs and tailors resumes to specific requirements
- **📄 Multiple Templates**: Harvard, Enhancv, and Resume.io templates
- **🔄 Smart Validation**: Robust validation with retry logic and error handling
- **📁 Organized Output**: Systematic folder structure for generated resumes
- **⚡ Fast & Efficient**: Timeout protection and fallback mechanisms

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** with Llama 3 8B model
3. **Required Python packages** (see requirements.txt)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd resume-builder
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama and Llama 3 8B:**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Llama 3 8B model
   ollama pull llama3:8b
   ```

4. **Create input files:**
   ```bash
   mkdir input
   # Create input/user_details.txt with your information
   # Create input/job_description.txt with job details
   ```

## 📖 Usage

### Method 1: Manual Job Description

```bash
python main.py --template harvard
```

### Method 2: Job URL Processing

```bash
# Single job URL
python resume_from_jobs.py --urls "https://linkedin.com/jobs/view/123456"

# Multiple job URLs
python resume_from_jobs.py --urls "https://linkedin.com/jobs/view/123456" "https://indeed.com/jobs/789012"

# From file
python resume_from_jobs.py --urls-file sample_urls.txt
```

### Method 3: Resume Management

```bash
# List generated resumes
python resume_manager.py --list

# Open specific resume
python resume_manager.py --open "resume_folder_name"

# Delete resume
python resume_manager.py --delete "resume_folder_name"
```

## 📁 Project Structure

```
resume-builder/
├── main.py                 # Main resume generator
├── generator.py            # LLM integration and data generation
├── validator.py            # Data validation (no modification)
├── renderer.py             # HTML template rendering
├── exporter.py             # PDF/HTML export
├── job_parser.py           # Job URL parsing
├── resume_from_jobs.py     # Batch job processing
├── resume_manager.py       # Resume management
├── templates/              # HTML templates
│   ├── template_harvard.html
│   ├── template_enhancv.html.html
│   └── template_resumeio.html
├── input/                  # Input files
│   ├── user_details.txt
│   └── job_description.txt
├── resumes/                # Generated resumes (auto-created)
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### LLM Settings (generator.py)
```python
LLM_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "llama3:8b",
    "temperature": 0.7,
    "max_tokens": 4000,
    "timeout": 120
}
```

### Validation Limits
- **Max attempts**: 2 validation attempts
- **Timeout**: 30 seconds per LLM call
- **Retries**: 2 API call retries

## 📝 Input Format

### user_details.txt
```
Name: Your Full Name
Email: your.email@example.com
Phone: +1-234-567-8900
LinkedIn: linkedin.com/in/yourprofile
GitHub: github.com/yourusername
Website: yourwebsite.com
Location: City, State
Job Title: Target Position
Summary: Professional summary

Skills: Python, JavaScript, React, Node.js, SQL

Experience:
- Software Engineer | Tech Corp | 2020-2023
  * Built web applications using React and Node.js
  * Improved performance by 40% through optimization
  * Led team of 3 developers

Education:
- Computer Science | University of Tech | 2020

Projects:
- E-commerce Platform | React, Node.js, MongoDB | Built full-stack e-commerce solution

Certifications: AWS Certified Developer, Google Cloud Professional
```

### job_description.txt
```
Software Engineer Position at Tech Company

We are looking for a skilled software engineer with experience in:
- Python and JavaScript
- React and Node.js
- Database design
- API development

Requirements:
- 3+ years of experience
- Bachelor's degree in Computer Science
- Strong problem-solving skills
```

## 🎯 Supported Job Sites

- **LinkedIn**: Full job details extraction
- **Indeed**: Job description and requirements
- **Glassdoor**: Company and role information
- **Monster**: Basic job details
- **Generic**: Fallback for other sites

## 🛡️ Error Handling

The system includes comprehensive error handling:

- **File errors**: Clear messages for missing/empty files
- **LLM failures**: Automatic fallback to text parsing
- **Validation errors**: Detailed error reporting
- **Network issues**: Retry logic with timeouts
- **Permission errors**: Graceful handling of file system issues

## 🔄 Flow Overview

```
1. Input Validation → Check files exist and have content
2. LLM Generation → Call Llama with timeout/retry protection  
3. JSON Extraction → Handle malformed responses gracefully
4. Data Validation → Check structure without modification
5. Retry Logic → Max 2 attempts, then terminate
6. File Operations → Handle permissions and errors
7. Output Generation → HTML/PDF with organized folders
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_complete_flow.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for local LLM hosting
- **Llama 3** by Meta for AI capabilities
- **Jinja2** for template rendering
- **WeasyPrint** for PDF generation

## 📞 Support

If you encounter any issues:

1. Check the error messages for guidance
2. Ensure Ollama is running with `ollama list`
3. Verify input file formats
4. Check the test suite: `python test_complete_flow.py`

---

**Happy Resume Building! 🚀**
