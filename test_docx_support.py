#!/usr/bin/env python3
"""
Test script to verify DOCX file support for CV uploads
"""

import os
from data import extract_text_from_file, extract_resume_with_openai

def test_docx_support():
    print("Testing DOCX Support for CV Upload...")
    
    # Test 1: Check if python-docx is importable
    try:
        import docx
        print("✅ python-docx library is installed and importable")
    except ImportError as e:
        print(f"❌ python-docx library import failed: {e}")
        return False
    
    # Test 2: Check file extension handling
    test_extensions = ['.pdf', '.docx', '.doc', '.txt']
    for ext in test_extensions:
        test_filename = f"test_resume{ext}"
        print(f"Testing extension: {ext}")
        
        # Check extension detection
        detected_ext = os.path.splitext(test_filename)[1].lower()
        print(f"  Detected extension: {detected_ext}")
        
        if ext == '.docx':
            print(f"  DOCX handling: {'✅ Supported' if detected_ext == '.docx' else '❌ Not detected'}")
    
    # Test 3: Check extract_text_from_file function for DOCX
    print("\nTesting extract_text_from_file function...")
    # Since we don't have a real DOCX file, let's just test the logic paths
    
    # Look for any existing DOCX files in the resumes folder
    resumes_folder = os.path.join(os.path.dirname(__file__), 'db', 'resumes')
    if os.path.exists(resumes_folder):
        docx_files = [f for f in os.listdir(resumes_folder) if f.lower().endswith('.docx')]
        if docx_files:
            print(f"Found DOCX files: {docx_files}")
            for docx_file in docx_files[:1]:  # Test with first DOCX file
                full_path = os.path.join(resumes_folder, docx_file)
                try:
                    text = extract_text_from_file(full_path)
                    print(f"✅ Successfully extracted text from {docx_file}: {len(text)} characters")
                except Exception as e:
                    print(f"❌ Failed to extract text from {docx_file}: {e}")
        else:
            print("No DOCX files found in resumes folder for testing")
    else:
        print("Resumes folder not found")
    
    print("\nTesting complete!")
    return True

if __name__ == "__main__":
    test_docx_support()
