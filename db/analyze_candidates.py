import json

# Load candidates data
with open('candidates.json', 'r') as f:
    candidates = json.load(f)

print("=== CANDIDATE ANALYSIS BY JOB ID ===\n")

# Group candidates by job_id
job_groups = {}
for candidate in candidates:
    job_id = candidate.get('job_id', 'Unknown')
    if job_id not in job_groups:
        job_groups[job_id] = []
    job_groups[job_id].append(candidate)

# Analyze each job
for job_id, job_candidates in sorted(job_groups.items()):
    print(f"🎯 JOB ID: {job_id}")
    print(f"   Total candidates: {len(job_candidates)}")
    
    # Count by status
    status_counts = {}
    for candidate in job_candidates:
        status = candidate.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("   Status breakdown:")
    for status, count in status_counts.items():
        print(f"     - {status}: {count}")
    
    print("   Candidate details:")
    for candidate in job_candidates:
        print(f"     • {candidate.get('name', 'Unknown')} - {candidate.get('status', 'Unknown')}")
    
    print("\n" + "-"*50 + "\n")
