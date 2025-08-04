#!/usr/bin/env python3
"""
Debug script to check vacancy calculations
"""
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def debug_vacancies():
    # Load jobs directly
    with open('db/jobs.json', 'r') as f:
        jobs = json.load(f)
    
    print(f"Total jobs in database: {len(jobs)}")
    
    total_all = 0
    total_open = 0
    total_closed = 0
    total_no_status = 0
    
    print("\nJob breakdown:")
    for job in jobs:
        job_id = job.get('job_id', 'Unknown')
        title = job.get('job_title', 'Unknown')[:30]
        status = job.get('status', 'No Status')
        openings = int(job.get('job_openings', 0))
        
        print(f"Job {job_id}: {title:<30} Status: {status:<10} Openings: {openings}")
        
        total_all += openings
        
        if status.lower() == 'open':
            total_open += openings
        elif status.lower() == 'closed':
            total_closed += openings
        else:
            total_no_status += openings
    
    print(f"\nSummary:")
    print(f"Total ALL vacancies: {total_all}")
    print(f"Total OPEN vacancies: {total_open}")
    print(f"Total CLOSED vacancies: {total_closed}")
    print(f"Total NO STATUS vacancies: {total_no_status}")
    
    # Test our functions
    from data import total_all_vacancies_count, open_vacancies_count, closed_vacancies_count
    
    print(f"\nFunction results:")
    print(f"total_all_vacancies_count(): {total_all_vacancies_count()}")
    print(f"open_vacancies_count(): {open_vacancies_count()}")
    print(f"closed_vacancies_count(): {closed_vacancies_count()}")

if __name__ == "__main__":
    debug_vacancies()
