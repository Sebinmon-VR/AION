import json
import random
from datetime import datetime, timedelta

def add_salary_data_to_candidates():
    """Add realistic salary data to hired candidates based on their positions and departments"""
    
    # Load candidates data
    with open('db/candidates.json', 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    # Salary ranges by position and seniority (in USD/month)
    salary_ranges = {
        'SP3D Designer': {'junior': (4500, 6000), 'mid': (6000, 8500), 'senior': (8500, 12000)},
        'SP3D Admin': {'junior': (4000, 5500), 'mid': (5500, 7500), 'senior': (7500, 10000)},
        'Piping Designer': {'junior': (4200, 5800), 'mid': (5800, 8000), 'senior': (8000, 11000)},
        'AutoCAD Designer': {'junior': (3500, 5000), 'mid': (5000, 7000), 'senior': (7000, 9500)},
        'Process Engineer': {'junior': (5000, 7000), 'mid': (7000, 9500), 'senior': (9500, 13000)},
        'Mechanical Engineer': {'junior': (4800, 6500), 'mid': (6500, 9000), 'senior': (9000, 12500)},
        'Electrical Engineer': {'junior': (5200, 7200), 'mid': (7200, 9800), 'senior': (9800, 13500)},
        'Project Manager': {'junior': (6000, 8000), 'mid': (8000, 11000), 'senior': (11000, 15000)},
        'Quality Engineer': {'junior': (4500, 6200), 'mid': (6200, 8500), 'senior': (8500, 11500)},
        'Safety Engineer': {'junior': (4600, 6400), 'mid': (6400, 8800), 'senior': (8800, 12000)},
        'Default': {'junior': (4000, 5500), 'mid': (5500, 7500), 'senior': (7500, 10500)}
    }
    
    # Department multipliers
    department_multipliers = {
        'Digital': 1.1,
        'Digitization': 1.1,
        'Mechanical': 1.0,
        'Electrical': 1.05,
        'Process': 1.08,
        'Civil': 0.95,
        'Safety': 1.02,
        'Quality': 0.98,
        'Project Management': 1.15
    }
    
    # Load jobs data to get department info
    with open('db/jobs.json', 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Create job lookup
    job_lookup = {job['job_id']: job for job in jobs}
    
    hired_count = 0
    updated_count = 0
    
    for candidate in candidates:
        if candidate.get('status') == 'Hired':
            hired_count += 1
            
            # Skip if salary data already exists
            if 'offered_salary' in candidate:
                continue
                
            # Get job details
            job_id = candidate.get('job_id', '1')
            job = job_lookup.get(job_id, {})
            
            # Determine position and seniority
            position = candidate.get('position', 'Default')
            department = job.get('department', 'Digital')
            seniority_level = job.get('seniority_level', 'Mid').lower()
            
            # Get base salary range
            position_key = position if position in salary_ranges else 'Default'
            seniority_key = seniority_level if seniority_level in ['junior', 'mid', 'senior'] else 'mid'
            
            base_min, base_max = salary_ranges[position_key][seniority_key]
            
            # Apply department multiplier
            dept_multiplier = department_multipliers.get(department, 1.0)
            adjusted_min = int(base_min * dept_multiplier)
            adjusted_max = int(base_max * dept_multiplier)
            
            # Generate offered salary (slightly random within range)
            offered_salary = random.randint(adjusted_min, adjusted_max)
            
            # Add small variation for negotiation
            final_salary = offered_salary + random.randint(-200, 500)
            
            # Generate benefits package (10-20% of salary)
            benefits_value = int(final_salary * random.uniform(0.10, 0.20))
            
            # Add salary data to candidate
            candidate['offered_salary'] = offered_salary
            candidate['negotiated_salary'] = final_salary
            candidate['final_salary'] = final_salary
            candidate['benefits_package'] = benefits_value
            candidate['total_compensation'] = final_salary + benefits_value
            candidate['salary_currency'] = 'USD'
            candidate['salary_period'] = 'Monthly'
            
            # Add offer details
            candidate['offer_details'] = {
                'base_salary': final_salary,
                'benefits': benefits_value,
                'bonus_eligible': random.choice([True, False]),
                'health_insurance': True,
                'paid_leave_days': random.randint(21, 30),
                'offer_date': candidate.get('selected_date', '2025-07-15'),
                'offer_accepted_date': candidate.get('hired_date', '2025-07-20')
            }
            
            # Add market comparison data
            market_avg = int(((adjusted_min + adjusted_max) / 2) * random.uniform(0.95, 1.10))
            candidate['market_comparison'] = {
                'market_average': market_avg,
                'our_offer': final_salary,
                'competitiveness': 'Above Market' if final_salary > market_avg else 'Below Market' if final_salary < market_avg * 0.95 else 'Market Rate'
            }
            
            updated_count += 1
    
    # Save updated data
    with open('db/candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Salary data added successfully!")
    print(f"📊 Total hired candidates: {hired_count}")
    print(f"🆕 Candidates updated with salary data: {updated_count}")
    print(f"📈 Salary ranges from ${min([c.get('final_salary', 0) for c in candidates if c.get('final_salary')])} to ${max([c.get('final_salary', 0) for c in candidates if c.get('final_salary')])}")

def add_onboarding_probation_data():
    """Add onboarding and probation data for better analytics"""
    
    with open('db/candidates.json', 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    for candidate in candidates:
        if candidate.get('status') == 'Hired' and 'onboarding_status' not in candidate:
            # Add onboarding data
            candidate['onboarding_status'] = random.choice(['Completed', 'In Progress', 'Delayed'])
            candidate['onboarding_completion_date'] = candidate.get('hired_date', '2025-07-20')
            
            # Add probation data
            candidate['probation_status'] = random.choice(['Passed', 'In Progress', 'Under Review'])
            candidate['probation_end_date'] = '2025-10-20'  # 3 months after hiring
            candidate['performance_rating'] = random.choice(['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'])
    
    # Save updated data
    with open('db/candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=4, ensure_ascii=False)
    
    print("✅ Onboarding and probation data added!")

if __name__ == "__main__":
    add_salary_data_to_candidates()
    add_onboarding_probation_data()
