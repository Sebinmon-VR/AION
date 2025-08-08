import json
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Test the milestone logic for hired candidates
def test_hired_milestone():
    try:
        # Load candidates
        with open('db/candidates.json', 'r') as f:
            candidates = json.load(f)
        
        label = 'hired'
        
        # Filter candidates for 'hired' status - this mimics the logic in milestones_breakup_label
        if label.lower() == 'hired':
            # Load all candidates from your data source (not just filtered)
            total_applicants = len(candidates)
            hired_candidates = [c for c in candidates if str(c.get('status', '')).lower() == 'hired']
            total_hired = len(hired_candidates)
            success_rate = round((total_hired / total_applicants) * 100, 1) if total_applicants else 0
            
            print(f"=== MILESTONE CALCULATION FOR 'hired' ===")
            print(f"Total applicants: {total_applicants}")
            print(f"Total hired: {total_hired}")
            print(f"Success rate: {success_rate}%")
            print(f"Hired candidates:")
            for c in hired_candidates:
                print(f"  - {c.get('name')} (Status: '{c.get('status')}')")
            
            # Check if template variables would be populated correctly
            print(f"\n=== TEMPLATE VARIABLES ===")
            print(f"{{ total_applicants }} = {total_applicants}")
            print(f"{{ total_hired }} = {total_hired}")
            print(f"{{ success_rate }} = {success_rate}")
            
            return {
                'total_applicants': total_applicants,
                'total_hired': total_hired,
                'success_rate': success_rate,
                'hired_candidates': hired_candidates
            }
        else:
            print("Label is not 'hired'")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = test_hired_milestone()
    if result and result['total_hired'] > 0:
        print(f"\n✅ SUCCESS: Found {result['total_hired']} hired candidate(s)")
        print("The /milestones_breakup/hired page should show this data")
    else:
        print("\n❌ ERROR: No hired candidates found")
