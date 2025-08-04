#!/usr/bin/env python3
"""
Quick test script to verify the openings_count function
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from data import openings_count, fetch_job_data

def test_openings_count():
    print("Testing openings_count function...")
    
    # Get all jobs
    jobs = fetch_job_data()
    print(f"Total jobs in database: {len(jobs)}")
    
    # Manual calculation
    total_manual = 0
    open_jobs = 0
    closed_jobs = 0
    no_status_jobs = 0
    
    print("\nJob breakdown:")
    for job in jobs:
        status = job.get('status', 'Open')  # Default to Open if no status
        openings = int(job.get('job_openings', 0))
        
        print(f"Job {job['job_id']}: {job['job_title'][:30]:<30} Status: {status:<6} Openings: {openings}")
        
        if status.lower() == 'open':
            total_manual += openings
            open_jobs += 1
        elif status.lower() == 'closed':
            closed_jobs += 1
        else:
            # Jobs without status field
            total_manual += openings
            no_status_jobs += 1
    
    # Get function result
    function_result = openings_count()
    
    print(f"\nSummary:")
    print(f"Open jobs: {open_jobs}")
    print(f"Closed jobs: {closed_jobs}")
    print(f"Jobs without status (treated as open): {no_status_jobs}")
    print(f"Manual calculation total: {total_manual}")
    print(f"Function result: {function_result}")
    print(f"Match: {'✓' if total_manual == function_result else '✗'}")

if __name__ == "__main__":
    test_openings_count()
