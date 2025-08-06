import json

# Load existing candidates
with open('candidates.json', 'r') as f:
    candidates = json.load(f)

# Add more candidates for different jobs to make data more realistic
new_candidates = [
    {
        "id": 9,
        "name": "Ahmed Al Mansouri",
        "email": "ahmed.mansouri@example.com",
        "phone": "+971-50-1111111",
        "position": "SP3D Designer",
        "status": "Applied",
        "applied_date": "2025-07-23",
        "job_id": "5"
    },
    {
        "id": 10,
        "name": "Noor Al Zahra",
        "email": "noor.alzahra@example.com",
        "phone": "+971-55-2222222",
        "position": "SP3D Designer",
        "status": "Shortlisted",
        "applied_date": "2025-07-22",
        "job_id": "5"
    },
    {
        "id": 11,
        "name": "Hassan Ali",
        "email": "hassan.ali@example.com",
        "phone": "+971-52-3333333",
        "position": "SP3D Designer",
        "status": "Interviewed",
        "applied_date": "2025-07-21",
        "job_id": "5"
    },
    {
        "id": 12,
        "name": "Maryam Ahmed",
        "email": "maryam.ahmed@example.com",
        "phone": "+971-50-4444444",
        "position": "SP3D Designer",
        "status": "Hired",
        "applied_date": "2025-07-20",
        "job_id": "5"
    },
    {
        "id": 13,
        "name": "Khalifa Rashid",
        "email": "khalifa.rashid@example.com",
        "phone": "+971-55-5555555",
        "position": "SP3D Designer",
        "status": "Applied",
        "applied_date": "2025-07-24",
        "job_id": "6"
    },
    {
        "id": 14,
        "name": "Fatma Hassan",
        "email": "fatma.hassan@example.com",
        "phone": "+971-52-6666666",
        "position": "SP3D Designer",
        "status": "Shortlisted",
        "applied_date": "2025-07-23",
        "job_id": "6"
    }
]

# Add new candidates to existing list
all_candidates = candidates + new_candidates

# Save updated candidates
with open('candidates.json', 'w') as f:
    json.dump(all_candidates, f, indent=4)

print("✅ Added new candidates for jobs 5 and 6")
print("\nUpdated candidate distribution:")

# Group by job_id and show distribution
job_groups = {}
for candidate in all_candidates:
    job_id = candidate.get('job_id', 'Unknown')
    if job_id not in job_groups:
        job_groups[job_id] = []
    job_groups[job_id].append(candidate)

for job_id, job_candidates in sorted(job_groups.items()):
    print(f"\n🎯 JOB ID: {job_id}")
    status_counts = {}
    for candidate in job_candidates:
        status = candidate.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
