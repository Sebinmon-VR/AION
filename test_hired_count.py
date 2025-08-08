import json

with open('db/candidates.json', 'r') as f:
    candidates = json.load(f)

print('Total candidates:', len(candidates))
hired_candidates = [c for c in candidates if c.get('status', '').lower() == 'hired']
print('Hired candidates:', len(hired_candidates))
for c in hired_candidates:
    print(f'- {c.get("name")} (Status: {c.get("status")})')
