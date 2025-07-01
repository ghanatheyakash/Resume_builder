#!/usr/bin/env python3
"""
Test script for Llama 3.2 8B integration with the resume builder.
"""

from generator import test_llama_connection, call_llama_api, generate_resume_json


def test_simple_generation():
    """Test simple text generation with Llama."""
    print("🧪 Testing simple text generation...")
    
    prompt = "Generate a simple JSON object with name and email fields."
    response = call_llama_api(prompt)
    
    if response:
        print("✅ Simple generation successful!")
        print(f"Response: {response[:200]}...")
        return True
    else:
        print("❌ Simple generation failed")
        return False


def test_resume_generation():
    """Test resume generation with sample data."""
    print("\n🧪 Testing resume generation...")
    
    # Sample user details
    user_details = """
Name: John Doe
Email: john.doe@email.com
Phone: (555) 123-4567
Location: San Francisco, CA
Summary: Experienced software engineer with 5+ years in full-stack development.

Skills: Python, JavaScript, React, Node.js, AWS

Experience:
- Senior Software Engineer | TechCorp | 2022-Present
  * Led development of microservices architecture
  * Mentored junior developers

Education:
- BS Computer Science | University of Technology | 2016-2020
"""
    
    # Sample job description
    job_description = """
Software Engineer Position at TechStartup

We are looking for a skilled software engineer with experience in:
- Python and JavaScript development
- React and Node.js frameworks
- Cloud technologies (AWS)
- Microservices architecture

Requirements:
- 3+ years of software development experience
- Strong problem-solving skills
- Experience with modern web technologies
- Ability to work in a fast-paced environment
"""
    
    try:
        resume_data = generate_resume_json(job_description, user_details)
        
        if resume_data and "name" in resume_data:
            print("✅ Resume generation successful!")
            print(f"Generated resume for: {resume_data.get('name', 'Unknown')}")
            print(f"Skills: {resume_data.get('skills', [])}")
            print(f"Experience entries: {len(resume_data.get('experience', []))}")
            return True
        else:
            print("❌ Resume generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during resume generation: {e}")
        return False


def main():
    """Main test function."""
    print("🤖 Llama 3.2 8B Integration Test")
    print("=" * 40)
    
    # Test 1: Connection
    print("🔗 Testing Llama connection...")
    if not test_llama_connection():
        print("❌ Connection test failed")
        return False
    
    # Test 2: Simple generation
    if not test_simple_generation():
        print("❌ Simple generation test failed")
        return False
    
    # Test 3: Resume generation
    if not test_resume_generation():
        print("❌ Resume generation test failed")
        return False
    
    print("\n🎉 All tests passed! Llama integration is working correctly.")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 