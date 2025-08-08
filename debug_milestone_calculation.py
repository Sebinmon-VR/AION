import json

# Load candidates data
with open('db/candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

print("=== MILESTONE CALCULATION ===")
# This is how milestones_breakup_label calculates it
total_applicants = len(candidates)
hired_candidates = [c for c in candidates if str(c.get('status', '')).lower() == 'hired']
total_hired = len(hired_candidates)
success_rate = round((total_hired / total_applicants) * 100, 1) if total_applicants else 0

print(f"Total candidates: {total_applicants}")
print(f"Hired candidates: {total_hired}")
print(f"Success rate: {success_rate}%")

print("\n=== DASHBOARD CALCULATION ===")
# This is how index() calculates it
total_hired_dashboard = sum(1 for c in candidates if c.get('status', '').lower() == 'hired')

print(f"Total hired (dashboard style): {total_hired_dashboard}")

print("\n=== DETAILED COMPARISON ===")
for i, candidate in enumerate(candidates):
    status = candidate.get('status', '')
    name = candidate.get('name', 'Unknown')
    
    milestone_check = str(status).lower() == 'hired'
    dashboard_check = status.lower() == 'hired'
    
    if milestone_check != dashboard_check:
        print(f"MISMATCH: {name} - status: '{status}' - milestone: {milestone_check}, dashboard: {dashboard_check}")
    elif milestone_check:
        print(f"HIRED: {name} - status: '{status}'")
