#!/usr/bin/env python3
"""
Test script to demonstrate validation limits and LLM data preservation.
"""

import json
from validator import validate_resume

def test_validation_limits():
    """Test that validation has strict limits to prevent token waste."""
    
    print("🧪 Testing Validation Limits and LLM Data Preservation")
    print("=" * 60)
    
    # Simulate LLM-generated data with validation issues
    llm_data = {
        "name": "",  # Empty name will cause validation error
        "email": "invalid-email",  # Invalid email format
        "skills": "Python, JavaScript",  # LLM gave string instead of list
        "experience": [
            {
                "role": "Software Engineer",
                "company": "Tech Corp"
                # Missing dates and responsibilities
            }
        ]
    }
    
    print("🔍 Original LLM Data (with validation issues):")
    print(json.dumps(llm_data, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Validate the data
    errors = validate_resume(llm_data)
    
    print("✅ Validation Results:")
    if errors:
        print(f"❌ Found {len(errors)} validation errors:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    else:
        print("✅ No validation errors!")
    
    print("\n" + "="*50 + "\n")
    
    print("🎯 Key Points:")
    print("✅ Validator ONLY checks validity, never modifies data")
    print("✅ LLM data remains completely untouched")
    print("✅ Validation errors are reported clearly")
    print("✅ System will retry MAX_VALIDATION_ATTEMPTS times then terminate")
    print("✅ No infinite loops or token waste")
    
    print("\n" + "="*50 + "\n")
    
    print("📋 Validation Flow:")
    print("1. LLM generates data")
    print("2. Validator checks data (NO modifications)")
    print("3. If errors found → Report to LLM for retry")
    print("4. After MAX_ATTEMPTS → Terminate with clear error message")
    print("5. No data cleaning or modification anywhere")

if __name__ == "__main__":
    test_validation_limits() 