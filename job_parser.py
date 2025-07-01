import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import json
from urllib.parse import urlparse
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JobDetails:
    """Data class to store parsed job details."""
    url: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    skills: List[str]
    experience_level: str
    job_type: str
    salary_range: str
    parsed_at: str


class JobParser:
    """Parser for extracting job details from various job posting websites."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def parse_urls(self, urls: List[str]) -> List[JobDetails]:
        """Parse multiple URLs and extract job details."""
        job_details = []
        
        for url in urls:
            try:
                print(f"Parsing: {url}")
                job_detail = self.parse_single_url(url)
                if job_detail:
                    job_details.append(job_detail)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                print(f"Error parsing {url}: {str(e)}")
                continue
                
        return job_details
    
    def parse_single_url(self, url: str) -> Optional[JobDetails]:
        """Parse a single URL and extract job details."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Determine the website type and use appropriate parser
            domain = urlparse(url).netloc.lower()
            
            if 'linkedin.com' in domain:
                return self._parse_linkedin(soup, url)
            elif 'indeed.com' in domain:
                return self._parse_indeed(soup, url)
            elif 'glassdoor.com' in domain:
                return self._parse_glassdoor(soup, url)
            elif 'monster.com' in domain:
                return self._parse_monster(soup, url)
            else:
                return self._parse_generic(soup, url)
                
        except Exception as e:
            print(f"Error parsing {url}: {str(e)}")
            return None
    
    def _parse_linkedin(self, soup: BeautifulSoup, url: str) -> JobDetails:
        """Parse LinkedIn job postings."""
        title = self._extract_text(soup, [
            'h1.job-details-jobs-unified-top-card__job-title',
            '.job-details-jobs-unified-top-card__job-title',
            'h1[data-test-id="job-details-jobs-unified-top-card__job-title"]'
        ])
        
        company = self._extract_text(soup, [
            '.job-details-jobs-unified-top-card__company-name',
            '[data-test-id="job-details-jobs-unified-top-card__company-name"]'
        ])
        
        location = self._extract_text(soup, [
            '.job-details-jobs-unified-top-card__bullet',
            '[data-test-id="job-details-jobs-unified-top-card__bullet"]'
        ])
        
        description = self._extract_text(soup, [
            '.job-details-jobs-unified-top-card__job-description',
            '.show-more-less-html__markup',
            '[data-test-id="job-details-jobs-unified-top-card__job-description"]'
        ])
        
        return JobDetails(
            url=url,
            title=title or "Unknown Title",
            company=company or "Unknown Company",
            location=location or "Unknown Location",
            description=description or "",
            requirements=self._extract_requirements(description),
            skills=self._extract_skills(description),
            experience_level=self._extract_experience_level(description),
            job_type=self._extract_job_type(description),
            salary_range=self._extract_salary_range(description),
            parsed_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _parse_indeed(self, soup: BeautifulSoup, url: str) -> JobDetails:
        """Parse Indeed job postings."""
        title = self._extract_text(soup, [
            'h1[data-testid="jobsearch-JobInfoHeader-title"]',
            '.jobsearch-JobInfoHeader-title',
            'h1'
        ])
        
        company = self._extract_text(soup, [
            '[data-testid="jobsearch-JobInfoHeader-companyName"]',
            '.jobsearch-JobInfoHeader-companyName'
        ])
        
        location = self._extract_text(soup, [
            '[data-testid="jobsearch-JobInfoHeader-locationText"]',
            '.jobsearch-JobInfoHeader-locationText'
        ])
        
        description = self._extract_text(soup, [
            '#jobDescriptionText',
            '.jobsearch-jobDescriptionText'
        ])
        
        return JobDetails(
            url=url,
            title=title or "Unknown Title",
            company=company or "Unknown Company",
            location=location or "Unknown Location",
            description=description or "",
            requirements=self._extract_requirements(description),
            skills=self._extract_skills(description),
            experience_level=self._extract_experience_level(description),
            job_type=self._extract_job_type(description),
            salary_range=self._extract_salary_range(description),
            parsed_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _parse_glassdoor(self, soup: BeautifulSoup, url: str) -> JobDetails:
        """Parse Glassdoor job postings."""
        title = self._extract_text(soup, [
            '.job-title',
            'h1',
            '[data-test="job-title"]'
        ])
        
        company = self._extract_text(soup, [
            '.employer-name',
            '[data-test="employer-name"]'
        ])
        
        location = self._extract_text(soup, [
            '.location',
            '[data-test="location"]'
        ])
        
        description = self._extract_text(soup, [
            '.jobDescriptionContent',
            '.desc'
        ])
        
        return JobDetails(
            url=url,
            title=title or "Unknown Title",
            company=company or "Unknown Company",
            location=location or "Unknown Location",
            description=description or "",
            requirements=self._extract_requirements(description),
            skills=self._extract_skills(description),
            experience_level=self._extract_experience_level(description),
            job_type=self._extract_job_type(description),
            salary_range=self._extract_salary_range(description),
            parsed_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _parse_monster(self, soup: BeautifulSoup, url: str) -> JobDetails:
        """Parse Monster job postings."""
        title = self._extract_text(soup, [
            '.job-title',
            'h1',
            '[data-testid="job-title"]'
        ])
        
        company = self._extract_text(soup, [
            '.company-name',
            '[data-testid="company-name"]'
        ])
        
        location = self._extract_text(soup, [
            '.location',
            '[data-testid="location"]'
        ])
        
        description = self._extract_text(soup, [
            '.job-description',
            '.description'
        ])
        
        return JobDetails(
            url=url,
            title=title or "Unknown Title",
            company=company or "Unknown Company",
            location=location or "Unknown Location",
            description=description or "",
            requirements=self._extract_requirements(description),
            skills=self._extract_skills(description),
            experience_level=self._extract_experience_level(description),
            job_type=self._extract_job_type(description),
            salary_range=self._extract_salary_range(description),
            parsed_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _parse_generic(self, soup: BeautifulSoup, url: str) -> JobDetails:
        """Generic parser for unknown job sites."""
        title = self._extract_text(soup, ['h1', '.title', '[class*="title"]'])
        company = self._extract_text(soup, ['.company', '[class*="company"]'])
        location = self._extract_text(soup, ['.location', '[class*="location"]'])
        description = self._extract_text(soup, ['.description', '[class*="description"]', 'body'])
        
        return JobDetails(
            url=url,
            title=title or "Unknown Title",
            company=company or "Unknown Company",
            location=location or "Unknown Location",
            description=description or "",
            requirements=self._extract_requirements(description),
            skills=self._extract_skills(description),
            experience_level=self._extract_experience_level(description),
            job_type=self._extract_job_type(description),
            salary_range=self._extract_salary_range(description),
            parsed_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _extract_text(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text using multiple CSS selectors."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""
    
    def _extract_requirements(self, description: str) -> List[str]:
        """Extract job requirements from description."""
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'requirements?[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'qualifications?[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'must have[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'required[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by bullet points or new lines
                items = re.split(r'[•\-\*]\s*|\n\s*[•\-\*]\s*', match)
                requirements.extend([item.strip() for item in items if item.strip()])
        
        return list(set(requirements))  # Remove duplicates
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract technical skills from description."""
        skills = []
        
        # Common technical skills
        tech_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch',
            'Machine Learning', 'AI', 'Data Science', 'DevOps', 'Agile', 'Scrum'
        ]
        
        description_lower = description.lower()
        for skill in tech_skills:
            if skill.lower() in description_lower:
                skills.append(skill)
        
        return skills
    
    def _extract_experience_level(self, description: str) -> str:
        """Extract experience level from description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return "Senior"
        elif any(word in description_lower for word in ['mid', 'intermediate', '3-5 years']):
            return "Mid-level"
        elif any(word in description_lower for word in ['junior', 'entry', '0-2 years', 'recent graduate']):
            return "Junior"
        else:
            return "Not specified"
    
    def _extract_job_type(self, description: str) -> str:
        """Extract job type from description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['remote', 'work from home', 'wfh']):
            return "Remote"
        elif any(word in description_lower for word in ['hybrid', 'partially remote']):
            return "Hybrid"
        elif any(word in description_lower for word in ['on-site', 'onsite', 'in-office']):
            return "On-site"
        else:
            return "Not specified"
    
    def _extract_salary_range(self, description: str) -> str:
        """Extract salary range from description."""
        salary_patterns = [
            r'\$[\d,]+(?:k|K)?\s*-\s*\$[\d,]+(?:k|K)?',
            r'\$[\d,]+(?:k|K)?\s*to\s*\$[\d,]+(?:k|K)?',
            r'salary[:\s]+.*?\$[\d,]+(?:k|K)?',
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return "Not specified"
    
    def save_to_json(self, job_details: List[JobDetails], filename: str = "parsed_jobs.json"):
        """Save parsed job details to JSON file."""
        data = []
        for job in job_details:
            data.append({
                'url': job.url,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'requirements': job.requirements,
                'skills': job.skills,
                'experience_level': job.experience_level,
                'job_type': job.job_type,
                'salary_range': job.salary_range,
                'parsed_at': job.parsed_at
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(data)} job details to {filename}")
    
    def generate_summary_report(self, job_details: List[JobDetails]) -> str:
        """Generate a summary report of all parsed jobs."""
        if not job_details:
            return "No jobs were successfully parsed."
        
        report = []
        report.append("=" * 60)
        report.append("JOB PARSING SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"Total jobs parsed: {len(job_details)}")
        report.append("")
        
        # Skills frequency analysis
        all_skills = []
        for job in job_details:
            all_skills.extend(job.skills)
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        if skill_counts:
            report.append("MOST REQUESTED SKILLS:")
            sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
            for skill, count in sorted_skills[:10]:
                report.append(f"  {skill}: {count} jobs")
            report.append("")
        
        # Experience level distribution
        exp_counts = {}
        for job in job_details:
            exp_counts[job.experience_level] = exp_counts.get(job.experience_level, 0) + 1
        
        report.append("EXPERIENCE LEVEL DISTRIBUTION:")
        for level, count in exp_counts.items():
            report.append(f"  {level}: {count} jobs")
        report.append("")
        
        # Job type distribution
        type_counts = {}
        for job in job_details:
            type_counts[job.job_type] = type_counts.get(job.job_type, 0) + 1
        
        report.append("JOB TYPE DISTRIBUTION:")
        for job_type, count in type_counts.items():
            report.append(f"  {job_type}: {count} jobs")
        report.append("")
        
        # Individual job summaries
        report.append("INDIVIDUAL JOB SUMMARIES:")
        report.append("-" * 60)
        
        for i, job in enumerate(job_details, 1):
            report.append(f"{i}. {job.title}")
            report.append(f"   Company: {job.company}")
            report.append(f"   Location: {job.location}")
            report.append(f"   Experience: {job.experience_level}")
            report.append(f"   Type: {job.job_type}")
            report.append(f"   Skills: {', '.join(job.skills[:5])}{'...' if len(job.skills) > 5 else ''}")
            report.append(f"   URL: {job.url}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run the job parser."""
    parser = JobParser()
    
    # Example usage
    print("Job Parser - Extract job details from multiple URLs")
    print("=" * 50)
    
    # Get URLs from user
    urls = []
    print("Enter job URLs (one per line, press Enter twice when done):")
    while True:
        url = input().strip()
        if not url:
            break
        if url.startswith(('http://', 'https://')):
            urls.append(url)
        else:
            print("Please enter a valid URL starting with http:// or https://")
    
    if not urls:
        print("No valid URLs provided. Exiting.")
        return
    
    print(f"\nParsing {len(urls)} URLs...")
    job_details = parser.parse_urls(urls)
    
    if job_details:
        # Save to JSON
        parser.save_to_json(job_details)
        
        # Generate and display summary report
        report = parser.generate_summary_report(job_details)
        print("\n" + report)
        
        # Save report to file
        with open("job_parsing_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        print("\nDetailed report saved to job_parsing_report.txt")
        
    else:
        print("No jobs were successfully parsed.")


if __name__ == "__main__":
    main() 