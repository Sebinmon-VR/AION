import os
import json


# ------------------------------------------------------------------------------------
def fetch_user_data():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    user_file = os.path.join(db_folder, 'userdata.json')
    user_data = []
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                user_data = []
    return user_data

def total_users():
    user_data = fetch_user_data()
    return len(user_data)

def edit_user_data(username, new_data):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    user_file = os.path.join(db_folder, 'userdata.json')
    user_data = fetch_user_data()
    updated = False
    for user in user_data:
        if user.get('username') == username:
            user.update(new_data)
            updated = True
            break
    if updated:
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=4)
    return updated



# ------------------------------------------------------------------------------------

def fetch_job_data():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    job_file = os.path.join(db_folder, 'jobs.json')
    job_data = []
    if os.path.exists(job_file):
        with open(job_file, 'r') as f:
            try:
                job_data = json.load(f)
            except json.JSONDecodeError:
                job_data = []
    return job_data

def job_count():
    return len(fetch_job_data())

def openings_count():
    job_data = fetch_job_data()
    openings_count = 0
    for job in job_data:
        if 'job opening' in job and isinstance(job['job opening'], int):
            openings_count += job['job opening']
    return openings_count

    
# ------------------------------------------------------------------------------------


def fetch_candidate_data():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    candidate_file = os.path.join(db_folder, 'candidates.json')
    candidate_data = []
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidate_data = json.load(f)
            except json.JSONDecodeError:
                candidate_data = []
    return candidate_data

def candidate_count():
    candidate_data = fetch_candidate_data()
    return len(candidate_data)

def edit_candidate_data(candidate_id, new_data):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    candidate_file = os.path.join(db_folder, 'candidates.json')
    candidate_data = fetch_candidate_data()
    updated = False
    for candidate in candidate_data:
        if candidate.get('id') == candidate_id:
            candidate.update(new_data)
            updated = True
            break
    if updated:
        with open(candidate_file, 'w') as f:
            json.dump(candidate_data, f, indent=4)
    return updated

def fetch_candidates_by_filter(**filters):
    """
    Fetch candidates matching all provided filter key-value pairs.

    Example:
        fetch_candidates_by_filter(status='active', department='HR')
    """
    candidate_data = fetch_candidate_data()
    filtered_candidates = []
    for candidate in candidate_data:
        if all(candidate.get(key) == value for key, value in filters.items()):
            filtered_candidates.append(candidate)
    return filtered_candidates



# ------------------------------------------------------------------------------------

def fetch_onboarding_data():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    onboarding_file = os.path.join(db_folder, 'onboarding.json')
    onboarding_data = []
    if os.path.exists(onboarding_file):
        with open(onboarding_file, 'r') as f:
            try:
                onboarding_data = json.load(f)
            except json.JSONDecodeError:
                onboarding_data = []
    return onboarding_data




# ------------------------------------------------------------------------------------
