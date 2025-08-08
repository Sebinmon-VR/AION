import json
import datetime

# Load jobs and candidates
with open('db/jobs.json', 'r') as f:
    jobs = json.load(f)

with open('db/candidates.json', 'r') as f:
    candidates = json.load(f)

print('=== DEBUGGING HIRING PACE ===')
print(f'Total jobs: {len(jobs)}')
print(f'Total candidates: {len(candidates)}')

# Check active jobs
active_jobs = []
for job in jobs:
    job_status = job.get('status', '').lower()
    if job_status not in ['closed', 'filled', 'cancelled']:
        active_jobs.append(job)

print(f'Active jobs (not closed/filled/cancelled): {len(active_jobs)}')

# Check jobs with valid posted_at dates
valid_posted_jobs = []
for job in active_jobs:
    posted_at = job.get('posted_at', '')
    if posted_at:
        valid_posted_jobs.append(job)

print(f'Active jobs with posted_at dates: {len(valid_posted_jobs)}')

# Check jobs that are 0+ weeks old (including same day)
week_old_jobs = []
for job in valid_posted_jobs:
    posted_at = job.get('posted_at', '')
    try:
        posted_date = datetime.datetime.strptime(posted_at.split(' ')[0], '%Y-%m-%d')
        weeks_elapsed = (datetime.datetime.now() - posted_date).days // 7
        if weeks_elapsed >= 0:  # Include same day jobs
            week_old_jobs.append(job)
            job_id = job.get('job_id')
            job_title = job.get('job_title')
            print(f'Job {job_id}: {job_title} - {weeks_elapsed} weeks old')
    except Exception as e:
        job_id = job.get('job_id')
        print(f'Error parsing date for job {job_id}: {e}')

print(f'Jobs that are 0+ weeks old: {len(week_old_jobs)}')

# Show sample jobs with their status
print('\n=== SAMPLE JOBS ===')
for i, job in enumerate(jobs[:5]):
    print(f'Job {job.get("job_id")}: {job.get("job_title")} - Status: {job.get("status")} - Posted: {job.get("posted_at")}')

print(f'\nIf week_old_jobs is 0, that explains why hiring_pace_details is empty')
