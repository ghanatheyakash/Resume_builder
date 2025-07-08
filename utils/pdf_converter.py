import pdfkit
import os
import sys

class PDFConverter:
    """Utility class for converting HTML files to PDF using wkhtmltopdf"""
    
    def __init__(self):
        # Common wkhtmltopdf installation paths on Windows
        self.possible_paths = [
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\wkhtmltopdf\bin\wkhtmltopdf.exe',
            'wkhtmltopdf.exe'  # If it's in PATH
        ]
        self.wkhtmltopdf_path = self.find_wkhtmltopdf()
    
    def find_wkhtmltopdf(self):
        """Find wkhtmltopdf executable"""
        for path in self.possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def convert_html_to_pdf(self, input_html, output_pdf, options=None):
        """
        Convert HTML file to PDF
        
        Args:
            input_html (str): Path to input HTML file
            output_pdf (str): Path for output PDF file
            options (dict): Optional wkhtmltopdf options
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.wkhtmltopdf_path:
            print("wkhtmltopdf not found in common locations!")
            print("\nPlease do one of the following:")
            print("1. Install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
            print("2. Add wkhtmltopdf to your system PATH")
            print("3. Update the possible_paths list in this script with the correct path")
            print("\nTo find your wkhtmltopdf path, run: where wkhtmltopdf")
            return False
        
        if not os.path.exists(input_html):
            print(f"Input HTML file not found: {input_html}")
            return False
        
        print(f"Found wkhtmltopdf at: {self.wkhtmltopdf_path}")
        config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        
        # Default options for better PDF output
        default_options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Merge with user-provided options
        if options:
            default_options.update(options)
        
        try:
            pdfkit.from_file(input_html, output_pdf, configuration=config, options=default_options)
            print(f"Successfully converted {input_html} to {output_pdf}")
            return True
        except Exception as e:
            print(f"Error converting to PDF: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure wkhtmltopdf is properly installed")
            print("2. Try running: wkhtmltopdf --version in command prompt")
            print("3. If the path above is incorrect, update the possible_paths list")
            return False

def convert_html_to_pdf(input_html, output_pdf, options=None):
    """
    Convenience function to convert HTML to PDF
    
    Args:
        input_html (str): Path to input HTML file
        output_pdf (str): Path for output PDF file
        options (dict): Optional wkhtmltopdf options
    
    Returns:
        bool: True if successful, False otherwise
    """
    converter = PDFConverter()
    return converter.convert_html_to_pdf(input_html, output_pdf, options)

if __name__ == "__main__":
    # Example usage
    input_html = 'resume.html'
    output_pdf = 'resume.pdf'
    
    success = convert_html_to_pdf(input_html, output_pdf)
    if success:
        print("PDF conversion completed successfully!")
    else:
        print("PDF conversion failed!")
        sys.exit(1) 