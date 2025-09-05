#!/usr/bin/env python3
"""
Test script for the Legal Document Analysis API
"""

import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_upload_and_analysis():
    """Test file upload and analysis workflow"""
    print("\nTesting upload and analysis workflow...")
    
    # Check if we have test files in the pdf_files directory
    pdf_dir = "/Users/averm234/Library/CloudStorage/OneDrive-UHG/Documents/GitHub/atm-ml-cpml-eni-claims-business-apis/pdf_files"
    
    if not os.path.exists(pdf_dir):
        print(f"PDF directory not found: {pdf_dir}")
        return False
    
    # Find the first PDF file
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found for testing")
        return False
    
    test_file = os.path.join(pdf_dir, pdf_files[0])
    print(f"Using test file: {test_file}")
    
    # Upload file
    print("Uploading file...")
    with open(test_file, 'rb') as f:
        files = {'files': (pdf_files[0], f, 'application/pdf')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.status_code} - {response.text}")
        return False
    
    upload_result = response.json()
    job_id = upload_result['job_id']
    print(f"Upload successful. Job ID: {job_id}")
    
    # Start analysis
    print("Starting analysis...")
    response = requests.post(f"{API_BASE_URL}/analyze/{job_id}")
    
    if response.status_code != 200:
        print(f"Analysis start failed: {response.status_code} - {response.text}")
        return False
    
    print("Analysis started successfully")
    
    # Poll for status
    print("Polling for status...")
    max_polls = 60  # 5 minutes max
    poll_count = 0
    
    while poll_count < max_polls:
        response = requests.get(f"{API_BASE_URL}/status/{job_id}")
        
        if response.status_code != 200:
            print(f"Status check failed: {response.status_code}")
            return False
        
        status = response.json()
        print(f"Status: {status['status']}, Progress: {status.get('progress', 0)}%")
        
        if status['status'] == 'completed':
            print("Analysis completed!")
            break
        elif status['status'] == 'failed':
            print(f"Analysis failed: {status.get('error', 'Unknown error')}")
            return False
        
        time.sleep(5)
        poll_count += 1
    
    if poll_count >= max_polls:
        print("Analysis timed out")
        return False
    
    # Get results
    print("Getting results...")
    response = requests.get(f"{API_BASE_URL}/results/{job_id}")
    
    if response.status_code != 200:
        print(f"Results retrieval failed: {response.status_code}")
        return False
    
    results = response.json()
    print("Results retrieved successfully!")
    print(f"Document summary: {results.get('document_summary', {}).get('case_title', 'N/A')}")
    print(f"Number of events: {len(results.get('events', []))}")
    print(f"Number of recommendations: {len(results.get('recommendations', []))}")
    
    # Test export
    print("Testing export...")
    response = requests.get(f"{API_BASE_URL}/export/{job_id}?format=json")
    
    if response.status_code == 200:
        print("Export successful!")
        # Save to file
        with open(f"test_export_{job_id}.json", 'wb') as f:
            f.write(response.content)
        print(f"Exported results saved to test_export_{job_id}.json")
    else:
        print(f"Export failed: {response.status_code}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Legal Document Analysis API Test")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("Health check failed!")
        return
    
    # Test upload and analysis
    if test_upload_and_analysis():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    main()
