#!/usr/bin/env python3
"""
Resume Manager
A utility script to manage and view generated resumes in the organized folder structure.
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class ResumeManager:
    """Manage and organize generated resumes."""
    
    def __init__(self, resumes_dir: str = "resumes"):
        self.resumes_dir = Path(resumes_dir)
        self.resumes_dir.mkdir(exist_ok=True)
    
    def list_resumes(self, show_details: bool = False) -> List[Dict]:
        """List all generated resumes with their details."""
        resumes = []
        
        if not self.resumes_dir.exists():
            print(f"No resumes directory found at {self.resumes_dir}")
            return resumes
        
        for folder in sorted(self.resumes_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if folder.is_dir():
                resume_info = self.get_resume_info(folder)
                if resume_info:
                    resumes.append(resume_info)
                    
                    if show_details:
                        self.print_resume_details(resume_info)
                    else:
                        self.print_resume_summary(resume_info)
        
        return resumes
    
    def get_resume_info(self, folder_path: Path) -> Dict:
        """Extract information about a resume from its folder."""
        info = {
            'folder': folder_path.name,
            'path': folder_path,
            'created': datetime.fromtimestamp(folder_path.stat().st_mtime),
            'files': [],
            'template': 'Unknown',
            'method': 'Unknown',
            'job_title': 'Unknown',
            'company': 'Unknown'
        }
        
        # Check for files in the folder
        for file_path in folder_path.iterdir():
            if file_path.is_file():
                info['files'].append(file_path.name)
                
                # Extract template from filename
                if file_path.name.startswith('resume_') and file_path.name.endswith('.html'):
                    template = file_path.name.replace('resume_', '').replace('.html', '')
                    info['template'] = template
                
                # Read generation info
                if file_path.name == 'generation_info.txt':
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            for line in content.split('\n'):
                                if line.startswith('Template:'):
                                    info['template'] = line.split(':', 1)[1].strip()
                                elif line.startswith('Method:'):
                                    info['method'] = line.split(':', 1)[1].strip()
                    except:
                        pass
                
                # Read job details for URL-parsed resumes
                if file_path.name == 'job_details.json':
                    try:
                        with open(file_path, 'r') as f:
                            job_data = json.load(f)
                            if isinstance(job_data, list) and len(job_data) > 0:
                                job = job_data[0]
                                info['job_title'] = job.get('title', 'Unknown')
                                info['company'] = job.get('company', 'Unknown')
                    except:
                        pass
        
        return info
    
    def print_resume_summary(self, resume_info: Dict) -> None:
        """Print a summary of a resume."""
        print(f"📁 {resume_info['folder']}")
        print(f"   📅 {resume_info['created'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   🎨 Template: {resume_info['template']}")
        print(f"   💼 {resume_info['job_title']} at {resume_info['company']}")
        print(f"   📋 Method: {resume_info['method']}")
        print()
    
    def print_resume_details(self, resume_info: Dict) -> None:
        """Print detailed information about a resume."""
        print("=" * 60)
        print(f"📁 FOLDER: {resume_info['folder']}")
        print(f"📅 CREATED: {resume_info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎨 TEMPLATE: {resume_info['template']}")
        print(f"💼 JOB: {resume_info['job_title']}")
        print(f"🏢 COMPANY: {resume_info['company']}")
        print(f"📋 METHOD: {resume_info['method']}")
        print(f"📂 PATH: {resume_info['path']}")
        print("\n📄 FILES:")
        for file in resume_info['files']:
            print(f"   • {file}")
        print("=" * 60)
        print()
    
    def open_resume(self, folder_name: str, file_type: str = 'html') -> bool:
        """Open a specific resume file."""
        folder_path = self.resumes_dir / folder_name
        
        if not folder_path.exists():
            print(f"❌ Resume folder '{folder_name}' not found.")
            return False
        
        # Look for the specified file type
        file_pattern = f"resume_*.{file_type}"
        matching_files = list(folder_path.glob(file_pattern))
        
        if not matching_files:
            print(f"❌ No {file_type} file found in {folder_name}")
            return False
        
        file_path = matching_files[0]
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            elif system == "Windows":
                subprocess.run(["start", str(file_path)], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path)])
            
            print(f"✅ Opened {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening file: {e}")
            print(f"📁 File location: {file_path}")
            return False
    
    def delete_resume(self, folder_name: str, confirm: bool = True) -> bool:
        """Delete a resume folder."""
        folder_path = self.resumes_dir / folder_name
        
        if not folder_path.exists():
            print(f"❌ Resume folder '{folder_name}' not found.")
            return False
        
        if confirm:
            print(f"🗑️  Are you sure you want to delete '{folder_name}'?")
            response = input("Type 'yes' to confirm: ")
            if response.lower() != 'yes':
                print("❌ Deletion cancelled.")
                return False
        
        try:
            import shutil
            shutil.rmtree(folder_path)
            print(f"✅ Deleted resume folder: {folder_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting folder: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get statistics about generated resumes."""
        resumes = self.list_resumes()
        
        stats = {
            'total_resumes': len(resumes),
            'templates_used': {},
            'methods_used': {},
            'recent_resumes': 0,
            'oldest_resume': None,
            'newest_resume': None
        }
        
        if not resumes:
            return stats
        
        # Count templates and methods
        for resume in resumes:
            template = resume['template']
            method = resume['method']
            
            stats['templates_used'][template] = stats['templates_used'].get(template, 0) + 1
            stats['methods_used'][method] = stats['methods_used'].get(method, 0) + 1
        
        # Find date range
        dates = [resume['created'] for resume in resumes]
        stats['oldest_resume'] = min(dates)
        stats['newest_resume'] = max(dates)
        
        # Count recent resumes (last 7 days)
        week_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = week_ago.replace(day=week_ago.day - 7)
        stats['recent_resumes'] = len([r for r in resumes if r['created'] >= week_ago])
        
        return stats
    
    def print_stats(self) -> None:
        """Print statistics about generated resumes."""
        stats = self.get_stats()
        
        print("📊 RESUME STATISTICS")
        print("=" * 40)
        print(f"📁 Total Resumes: {stats['total_resumes']}")
        print(f"🆕 Recent (7 days): {stats['recent_resumes']}")
        
        if stats['oldest_resume'] and stats['newest_resume']:
            print(f"📅 Date Range: {stats['oldest_resume'].strftime('%Y-%m-%d')} to {stats['newest_resume'].strftime('%Y-%m-%d')}")
        
        print("\n🎨 Templates Used:")
        for template, count in stats['templates_used'].items():
            print(f"   • {template}: {count}")
        
        print("\n📋 Methods Used:")
        for method, count in stats['methods_used'].items():
            print(f"   • {method}: {count}")
        print()


def main():
    """Main function for the resume manager."""
    parser = argparse.ArgumentParser(description='Manage and view generated resumes')
    parser.add_argument('--list', '-l', action='store_true', help='List all resumes')
    parser.add_argument('--details', '-d', action='store_true', help='Show detailed information')
    parser.add_argument('--open', '-o', metavar='FOLDER', help='Open a specific resume folder')
    parser.add_argument('--file-type', choices=['html', 'pdf'], default='html', 
                       help='File type to open (default: html)')
    parser.add_argument('--delete', metavar='FOLDER', help='Delete a resume folder')
    parser.add_argument('--stats', '-s', action='store_true', help='Show statistics')
    parser.add_argument('--resumes-dir', default='resumes', help='Resumes directory (default: resumes)')
    
    args = parser.parse_args()
    
    manager = ResumeManager(args.resumes_dir)
    
    if args.stats:
        manager.print_stats()
    elif args.open:
        manager.open_resume(args.open, args.file_type)
    elif args.delete:
        manager.delete_resume(args.delete)
    elif args.list or not any([args.open, args.delete, args.stats]):
        manager.list_resumes(args.details)


if __name__ == "__main__":
    main() 