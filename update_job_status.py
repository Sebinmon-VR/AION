import json
import os

# Update jobs.json to change empty/no status to "open"
db_folder = os.path.join(os.path.dirname(__file__), 'db')
jobs_file = os.path.join(db_folder, 'jobs.json')

if os.path.exists(jobs_file):
    with open(jobs_file, 'r') as f:
        jobs = json.load(f)
    
    updated_count = 0
    for job in jobs:
        status = job.get('status', '')
        if not status or status.strip() == '':
            job['status'] = 'open'
            updated_count += 1
            print(f"Updated job {job.get('job_id')} - {job.get('job_title')} to 'open' status")
    
    # Save updated jobs
    with open(jobs_file, 'w') as f:
        json.dump(jobs, f, indent=2)
    
    print(f"Updated {updated_count} jobs to 'open' status")
else:
    print("jobs.json file not found")
