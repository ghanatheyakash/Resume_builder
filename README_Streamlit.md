# 📄 AI Resume Builder - Streamlit App

A modern web application that automatically generates tailored resumes from job descriptions using AI.

## 🚀 Features

- **Automatic Role & Company Extraction**: Parses job descriptions to extract role and company names
- **Real-time PDF Preview**: View generated resumes directly in the browser
- **One-click Download**: Download PDF resumes with proper naming
- **Custom Resume Data**: Upload your own resume JSON data or use the default
- **Professional Styling**: Clean, professional resume templates

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Ensure wkhtmltopdf is installed** (for PDF generation):
   - Download from: https://wkhtmltopdf.org/downloads.html
   - Add to system PATH or the app will detect it automatically

## 🔑 Setup Your Personal Information

### Step 1: Get Your Resume in JSON Format
1. **Use ChatGPT** to convert your resume to JSON format:
   - Copy your resume text
   - Ask ChatGPT: *"Convert my resume to JSON format with this structure: header (full_name, title, email, phone, linkedin, github), technical_skills (languages, tools_technologies, ides_text_editors, cloud, automation_tools, olap_tools, databases, web_development, python_programming_skills), education (institution, location, degree, start_year, end_year), career_objective, professional_summary (array of strings), work_experience (array with title, company, description, environment, location, dates, key_responsibilities)"*

2. **Replace the default resume.json**:
   - Open `resume.json` in the project root
   - Replace all content with your ChatGPT-generated JSON
   - Save the file

### Step 2: Update API Key
1. **Get your Gemini API key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key

2. **Replace the placeholder**:
   - Open `resume_optimizer.py`
   - Find line 136: `api_key = "paste your api key here"`
   - Replace `"paste your api key here"` with your actual API key
   - Example: `api_key = "AIzaSyYourActualAPIKeyHere"`

## 🎯 How to Use

1. **Start the App**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open in Browser**: The app will open at `http://localhost:8501`

3. **Input Job Description**: Paste the complete job description in the sidebar

4. **Generate Resume**: Click "Generate Resume" to create a tailored resume

5. **Preview & Download**: View the PDF preview and download the final resume

## 📋 App Interface

### Sidebar
- **Job Description**: Paste the job description here
- **Resume Data**: Upload custom JSON resume data (optional)
- **Generate Button**: Create the tailored resume

### Main Area
- **Job Details**: Shows extracted role and company
- **Resume Preview**: Displays the generated PDF
- **Download**: One-click download with proper naming

## 🔧 Technical Details

- **Backend**: Python with Streamlit
- **PDF Generation**: wkhtmltopdf via pdfkit
- **Template Engine**: Jinja2
- **File Organization**: Automatic role/company-based naming
- **AI Model**: Google Gemini 2.0 Flash

## 📁 File Structure

```
resume builder/
├── streamlit_app.py              # Main Streamlit application
├── requirements_streamlit.txt    # Streamlit dependencies
├── resume_optimizer.py          # Core resume optimization logic
├── resume_to_html.py            # HTML generation logic
├── resume.json                  # Your personal resume data (UPDATE THIS)
├── utils/pdf_converter.py       # PDF conversion utilities
└── resumes/                     # Generated resume folders
    └── Role_Company/
        ├── Resume.html
        ├── Resume.pdf
        └── job_description.txt
```

## 🎨 Customization

### Resume Template
The app uses the same professional template as the command-line version. To customize:
1. Edit the `TEMPLATE` variable in `resume_to_html.py`
2. Modify CSS styles for different appearance

### Resume Data
- **Update `resume.json`** with your personal information using ChatGPT
- The app will use your data to generate tailored resumes
- Ensure your JSON follows the required structure

## 🚨 Troubleshooting

### API Key Issues
- Make sure you've replaced the placeholder API key in `resume_optimizer.py`
- Verify your Gemini API key is valid and has sufficient quota
- Check that the API key is properly formatted

### Resume JSON Issues
- Ensure your JSON is valid (use a JSON validator)
- Follow the exact structure shown in the example
- Make sure all required fields are present

### PDF Generation Issues
- Ensure wkhtmltopdf is installed and in PATH
- Check that the job description contains clear role/company information
- Verify resume JSON data is properly formatted

### App Not Starting
- Check all dependencies are installed: `pip install -r requirements_streamlit.txt`
- Ensure no other process is using port 8501
- Check Python version compatibility (3.8+ recommended)

## 📝 Example Usage

1. **Update your resume data** in `resume.json`
2. **Replace the API key** in `resume_optimizer.py`
3. **Copy a job description** from any job posting
4. **Paste it** into the Streamlit app
5. **Click "Generate Resume"**
6. **Preview the PDF** in the browser
7. **Download** the tailored resume

The app will automatically:
- Extract "Data Scientist" and "Google" from "As a Data Scientist at Google..."
- Generate a resume named "Data_Scientist_Google_Resume.pdf"
- Provide instant preview and download

## 🔄 Integration with Existing Workflow

This Streamlit app works alongside your existing command-line tools:
- Uses the same resume generation logic
- Maintains the same file organization structure
- Compatible with all existing resume data and templates

Perfect for quick resume generation and preview without command-line interaction! 