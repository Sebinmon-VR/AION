import json
import datetime

# Load jobs and candidates
with open('db/jobs.json', 'r') as f:
    jobs = json.load(f)

with open('db/candidates.json', 'r') as f:
    candidates = json.load(f)

print('=== SIMULATING HIRING PACE TEMPLATE DATA ===')

# Simulate the exact logic from milestones_breakup_label route
hiring_pace_details = []
for job in jobs:
    job_status = job.get('status', '').lower()
    if job_status in ['closed', 'filled', 'cancelled']:
        continue
    
    posted_at = job.get('posted_at', '')
    if not posted_at:
        continue
    
    try:
        posted_date = datetime.datetime.strptime(posted_at.split(' ')[0], '%Y-%m-%d')
        weeks_elapsed = (datetime.datetime.now() - posted_date).days // 7
        
        if weeks_elapsed < 0:  # Updated logic
            continue
        
        job_id = job.get('job_id')
        job_candidates = [c for c in candidates if str(c.get('job_id')) == str(job_id)]
        
        max_stages = 0
        candidate_status = 'No applicants'
        if job_candidates:
            for candidate in job_candidates:
                stages = 0
                status = candidate.get('status', '').lower()
                
                # Stage counting logic from the route
                if status in ['new', 'shortlisted', 'interview scheduled', 'interviewed', 'pending approval', 'approved', 'selected', 'hired']:
                    stages += 1
                if status in ['interviewed', 'pending approval', 'approved', 'selected', 'hired']:
                    stages += 1
                if status in ['approved', 'selected', 'hired']:
                    stages += 1
                if status in ['hired']:
                    stages += 1
                if status == 'hired' and candidate.get('onboarding'):
                    onboarding_started = any(v == 'Completed' for v in candidate.get('onboarding', {}).values())
                    if onboarding_started:
                        stages += 1
                
                if stages > max_stages:
                    max_stages = stages
                    candidate_status = status.title()
        
        # Determine pace
        pace = 'Inadequate'
        if weeks_elapsed <= 2:
            if max_stages >= 3:
                pace = 'Excellent'
            elif max_stages >= 2:
                pace = 'Good'
            else:
                pace = 'Adequate'
        elif weeks_elapsed <= 4:
            if max_stages >= 4:
                pace = 'Good'
            elif max_stages >= 3:
                pace = 'Adequate'
        elif weeks_elapsed <= 10:
            if max_stages >= 5:
                pace = 'Good'
            elif max_stages >= 4:
                pace = 'Adequate'
        else:
            if max_stages >= 5:
                pace = 'Adequate'
        
        hiring_pace_details.append({
            'job_title': job.get('job_title', ''),
            'department': job.get('department', 'Unknown'),
            'posted_at': posted_at.split(' ')[0],
            'weeks_elapsed': weeks_elapsed,
            'stages_completed': max_stages,
            'candidate_status': candidate_status,
            'pace': pace,
            'applicants_count': len(job_candidates)
        })
        
        print(f'Job {job_id}: {job.get("job_title")} - {len(job_candidates)} candidates, {max_stages} stages, pace: {pace}')
        
    except (ValueError, Exception) as e:
        print(f'Error processing job {job.get("job_id")}: {e}')

print(f'\nTotal hiring_pace_details entries: {len(hiring_pace_details)}')

if len(hiring_pace_details) > 0:
    print('✅ Template should show the hiring pace table')
else:
    print('❌ Template will show "No active job postings" message')
