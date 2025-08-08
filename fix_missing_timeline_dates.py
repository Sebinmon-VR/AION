#!/usr/bin/env python3
"""
Fix missing timeline date fields for existing candidates.
This script extracts dates from status_history to populate missing date fields.
"""
import json
import os
from datetime import datetime

def fix_candidate_timeline_dates():
    """
    Fix missing timeline date fields by extracting dates from status_history
    """
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    candidate_file = os.path.join(db_folder, 'candidates.json')
    
    if not os.path.exists(candidate_file):
        print("❌ candidates.json not found")
        return
    
    # Load candidates
    with open(candidate_file, 'r') as f:
        try:
            candidates = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error reading candidates.json")
            return
    
    updated_count = 0
    
    for candidate in candidates:
        candidate_id = candidate.get('id', 'Unknown')
        candidate_name = candidate.get('name', 'Unknown')
        status_history = candidate.get('status_history', [])
        
        # Check if we need to fix any date fields
        needs_update = False
        updates_made = []
        
        # Map of status to date field name
        status_date_mapping = {
            'Shortlisted': 'shortlisted_date',
            'Interview Scheduled': 'interview_scheduled_date', 
            'Interviewed': 'interviewed_date',
            'Approved': 'approved_date',
            'Selected': 'selected_date',
            'Hired': 'hired_date',
            'Onboarding': 'onboarding_date'
        }
        
        # Process each status in history
        for history_entry in status_history:
            to_status = history_entry.get('to_status', '')
            updated_at = history_entry.get('updated_at', '')
            
            if to_status in status_date_mapping:
                date_field = status_date_mapping[to_status]
                
                # Check if this date field is missing
                if date_field not in candidate:
                    # Extract date from timestamp
                    try:
                        # Parse ISO format timestamp and extract date
                        if updated_at:
                            dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            date_str = dt.strftime('%Y-%m-%d')
                            candidate[date_field] = date_str
                            needs_update = True
                            updates_made.append(f"{to_status} -> {date_field} = {date_str}")
                    except Exception as e:
                        print(f"⚠️  Could not parse date for {candidate_name} ({candidate_id}): {e}")
        
        if needs_update:
            updated_count += 1
            print(f"✅ Updated {candidate_name} (ID: {candidate_id}):")
            for update in updates_made:
                print(f"   {update}")
    
    if updated_count > 0:
        # Save updated candidates
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        
        print(f"\n🎉 Successfully updated {updated_count} candidates with missing timeline dates")
        print("💾 Changes saved to candidates.json")
    else:
        print("✨ No candidates needed timeline date updates")

if __name__ == "__main__":
    print("🔧 Fixing missing timeline dates for existing candidates...")
    fix_candidate_timeline_dates()
    print("✅ Timeline date fix completed!")
