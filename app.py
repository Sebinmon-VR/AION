from flask import send_from_directory
# ---------------------------------------------------------------------------------------------------------------------


import threading
from flask import flash, jsonify
from werkzeug.utils import secure_filename
import markdown

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
from flask import Flask, request, jsonify, render_template, redirect, url_for
from Aion import chat_with_bot, SYSTEM_PROMPT
from flask_cors import CORS
import glob
import os
import json
import hashlib
import datetime
import sys
from dotenv import load_dotenv
from data import *
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

load_dotenv(override=True)
app = Flask(__name__)
CORS(app)   
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

db_folder = os.path.join(os.path.dirname(__file__), 'db')

jobs_file = os.path.join(db_folder, 'jobs.json')
# Upcoming Events API for chatbot and dashboard
@app.route('/upcoming_events')
def upcoming_events():
    try:
        events = fetch_all_upcoming_events(limit=30)
        # If the request is from the chatbot (expects JSON), return JSON
        if 'application/json' in request.headers.get('Accept', '') or request.args.get('format') == 'json':
            return jsonify({'upcoming_events': events})
        # Otherwise, render a template (optional, or just return JSON)
        return render_template('upcoming_events.html', upcoming_events=events, role=request.cookies.get('role', ''))
    except Exception as e:
        print(f"[ERROR] Failed to fetch upcoming events: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# Route to serve uploaded files (CVs, JDs, etc.) from the db directory
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    # Only allow serving files from db subfolders (resumes, jd_files, etc.)
    return send_from_directory(db_folder, filename)
# Breakdown page for radar chart labels
from flask import render_template
# Milestone-specific breakdown page
@app.route('/milestones_breakup/<label>')
def milestones_breakup_label(label):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    candidates_file = os.path.join(db_folder, 'candidates.json')
    jobs_file = os.path.join(db_folder, 'jobs.json')
    label_map = {
        'New': 'New',
        'Shortlisted': 'Shortlisted',
        'Interviewed': 'Interviewed',
        'Approved': 'Approved',
        'Hired': 'Hired',
        'Active applicants': 'Active Applicants',
        'Total applicants': 'Total Applicants'
    }
    status = label_map.get(label.lower(), label)
    candidates = []
    jobs = []
    if os.path.exists(candidates_file):
        with open(candidates_file, 'r') as f:
            try:
                candidates = json.load(f)
            except Exception:
                candidates = []
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            try:
                jobs = json.load(f)
            except Exception:
                jobs = []
    # Filtering logic
    if label.lower() == 'total_applicants':
        filtered_candidates = candidates
    elif label.lower() == 'active_applicants':
        filtered_candidates = [c for c in candidates if str(c.get('status', '')).strip().lower() not in ['resigned', 'fired']]
    elif label.lower() == 'attrition_score':
        filtered_candidates = [c for c in candidates if str(c.get('status', '')).strip().lower() in ['resigned', 'fired']]
    else:
        filtered_candidates = [c for c in candidates if str(c.get('status', '')).strip().lower() == status.lower()]
    # Department analytics (department only, not position, fallback to job's department)
    dept_data = {}
    # Build job_id to department map
    job_id_to_dept = {str(j.get('job_id')): j.get('department', 'Unknown') for j in jobs}
    all_departments = sorted(set(j.get('department', 'Unknown') for j in jobs))
    dept_data = {dept: 0 for dept in all_departments}
    for c in filtered_candidates:
        job_id = c.get('job_id')
        dept = job_id_to_dept.get(str(job_id), None) if job_id is not None else None
        if not dept:
            dept = c.get('department') or c.get('position') or 'Unknown'
        if dept in dept_data:
            dept_data[dept] += 1
        else:
            dept_data[dept] = 1
    dept_labels = list(dept_data.keys())
    dept_counts = list(dept_data.values())
    # Candidate table (all filtered candidates, with department info)
    display_candidates = []
    for c in filtered_candidates:
        job_id = c.get('job_id')
        dept = job_id_to_dept.get(str(job_id), None) if job_id is not None else None
        if not dept:
            dept = c.get('department') or c.get('position') or 'Unknown'
        job_title = None
        if job_id is not None:
            job = next((j for j in jobs if str(j.get('job_id')) == str(job_id)), None)
            if job:
                job_title = job.get('job_title', 'Unknown')
        display_candidates.append({
            'name': c.get('name', ''),
            'job_title': job_title or '',
            'department': dept,
            'status': c.get('status', ''),
            'applied_date': c.get('applied_date', ''),
            'id': c.get('id'),
        })
    import json as pyjson
    # Calculate analytics for 'hired' milestone
    total_applicants = total_hired = success_rate = 0
    if label.lower() == 'hired':
        # Load all candidates from your data source (not just filtered)
        with open(candidates_file, 'r', encoding='utf-8') as f:
            all_candidates = json.load(f)
        total_applicants = len(all_candidates)
        hired_candidates = [c for c in all_candidates if str(c.get('status', '')).lower() == 'hired']
        total_hired = len(hired_candidates)
        success_rate = round((total_hired / total_applicants) * 100, 1) if total_applicants else 0
    return render_template('milestones_breakup.html',
        label=label,
        dept_labels_json=pyjson.dumps(dept_labels),
        dept_counts_json=pyjson.dumps(dept_counts),
        candidates_json=pyjson.dumps(display_candidates),
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        display_candidates=display_candidates,
        total_applicants=total_applicants,
        total_hired=total_hired,
        success_rate=success_rate
    )

@app.route('/breakdown/<label>')
def breakdown(label):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    candidates_file = os.path.join(db_folder, 'candidates.json')
    jobs_file = os.path.join(db_folder, 'jobs.json')
    label_normalized = label.replace('_', ' ').strip().lower()
    label_normalized = label.replace('_', ' ').strip().lower()
    label_map = {
        'active applicants': 'Active Applicants',
        'new': 'New',
        'shortlisted': 'Shortlisted',
        'interviewed': 'Interviewed',
        'approved': 'Approved',
        'ready to hire': 'Selected',
        'hired': 'Hired'
    }
    status = label_map.get(label_normalized, label)
    candidates = []
    jobs = []
    if os.path.exists(candidates_file):
        with open(candidates_file, 'r') as f:
            try:
                candidates = json.load(f)
            except Exception:
                candidates = []
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            try:
                jobs = json.load(f)
            except Exception:
                jobs = []
    # Build job_id to department map (always)
    job_id_to_dept = {str(j.get('job_id')): j.get('department', 'Unknown') for j in jobs}
    # Filtering logic
    if label_normalized == 'active applicants':
        filtered_candidates = [c for c in candidates if str(c.get('status', '')).strip().lower() not in ['resigned', 'fired']]
    else:
        filtered_candidates = [c for c in candidates if str(c.get('status', '')).strip().lower() == status.lower()]
    # Department and job analytics
    # Get all departments from jobs (or hardcode if needed)
    all_departments = sorted(set(j.get('department', 'Unknown') for j in jobs))
    dept_data = {dept: 0 for dept in all_departments}
    job_data = {}
    for c in filtered_candidates:
        job_id = c.get('job_id')
        dept = job_id_to_dept.get(str(job_id), None) if job_id is not None else None
        if not dept:
            dept = c.get('department') or c.get('position') or 'Unknown'
        if dept in dept_data:
            dept_data[dept] += 1
        else:
            dept_data[dept] = 1
        job_title = None
        if job_id is not None:
            job = next((j for j in jobs if str(j.get('job_id')) == str(job_id)), None)
            if job:
                job_title = job.get('job_title', 'Unknown')
        if job_title:
            job_data[job_title] = job_data.get(job_title, 0) + 1
    dept_labels = list(dept_data.keys())
    dept_counts = list(dept_data.values())
    job_labels = list(job_data.keys())
    job_counts = list(job_data.values())
    # Candidate table
    display_candidates = []
    for c in filtered_candidates:
        job_id = c.get('job_id')
        dept = job_id_to_dept.get(str(job_id), None) if job_id is not None else None
        if not dept:
            dept = c.get('department') or c.get('position') or 'Unknown'
        job_title = None
        if job_id is not None:
            job = next((j for j in jobs if str(j.get('job_id')) == str(job_id)), None)
            if job:
                job_title = job.get('job_title', 'Unknown')
        # For 'hired', add date_of_joining if present
        candidate_dict = {
            'name': c.get('name', ''),
            'job_title': job_title or '',
            'department': dept,
            'status': c.get('status', ''),
            'applied_date': c.get('applied_date', ''),
            'id': c.get('id'),
        }
        if label.lower() == 'hired':
            candidate_dict['date_of_joining'] = c.get('date_of_joining', '')
        display_candidates.append(candidate_dict)
    total_candidates = len(display_candidates)
    # Top department and job
    top_dept = max(dept_data.items(), key=lambda x: x[1])[0] if dept_data else 'N/A'
    top_job = max(job_data.items(), key=lambda x: x[1])[0] if job_data else 'N/A'
    top_dept_pct = round(100 * dept_data.get(top_dept, 0) / total_candidates, 1) if total_candidates and top_dept != 'N/A' else 0
    top_job_pct = round(100 * job_data.get(top_job, 0) / total_candidates, 1) if total_candidates and top_job != 'N/A' else 0
    # --- Add analytics for 'hired' milestone ---
    total_applicants = total_hired = success_rate = 0
    dept_hired_labels = []
    dept_hired_counts = []
    if label.lower() == 'hired':
        # Load all candidates from your data source (not just display_candidates, which are filtered)
        with open('db/candidates.json', 'r', encoding='utf-8') as f:
            all_candidates = json.load(f)
        total_applicants = len(all_candidates)
        hired_candidates = [c for c in all_candidates if str(c.get('status', '')).lower() == 'hired']
        total_hired = len(hired_candidates)
        success_rate = round((total_hired / total_applicants) * 100, 1) if total_applicants else 0
        from collections import Counter
        def get_candidate_dept(c):
            dept = c.get('department')
            if not dept or dept == 'Unknown':
                dept = job_id_to_dept.get(str(c.get('job_id')), 'Unknown')
            return dept or 'Unknown'
        dept_counter = Counter(get_candidate_dept(c) for c in hired_candidates)
        dept_hired_labels = list(dept_counter.keys())
        dept_hired_counts = list(dept_counter.values())
    return render_template(
        'breakdown.html',
        label=label,
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        job_labels=job_labels,
        job_counts=job_counts,
        display_candidates=display_candidates,
        total_candidates=total_candidates,
        top_dept=top_dept,
        top_job=top_job,
        top_dept_pct=top_dept_pct,
        top_job_pct=top_job_pct,
        total_applicants=total_applicants,
        total_hired=total_hired,
        success_rate=success_rate,
        dept_hired_labels=dept_hired_labels,
        dept_hired_counts=dept_hired_counts,
        dept_data=dept_data,
        job_data=job_data
    )
# --- Search, Customization, and Templates Pages ---
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        # Example: search jobs and candidates (simple demo, replace with real logic)
        db_folder = os.path.join(os.path.dirname(__file__), 'db')
        jobs_file = os.path.join(db_folder, 'jobs.json')
        candidates_file = os.path.join(db_folder, 'candidates.json')
        if os.path.exists(jobs_file):
            with open(jobs_file, 'r') as f:
                try:
                    jobs = json.load(f)
                except Exception:
                    jobs = []
            for job in jobs:
                if query.lower() in str(job).lower():
                    results.append(f"Job: {job.get('job_title', '')}")
        if os.path.exists(candidates_file):
            with open(candidates_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except Exception:
                    candidates = []
            for cand in candidates:
                if query.lower() in str(cand).lower():
                    results.append(f"Candidate: {cand.get('name', '')}")
    return render_template('search.html', results=results, role=request.cookies.get('role', ''))

@app.route('/customization', methods=['GET', 'POST'])
def customization():
    all_menu_options = [
        'Dashboard', 'Post Jobs', 'Jobs', 'Manage Candidates', 'Manage Onboarding', 'Manage Team', 'Approve Hiring', 'Manage Admins', 'View All HR'
    ]
    role = request.cookies.get('role', '')
    username = request.cookies.get('username', '')
    user_file = os.path.join(db_folder, 'userdata.json')
    user_menu_order = None
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            try:
                users = json.load(f)
            except Exception:
                users = []
        user = next((u for u in users if u.get('username') == username), None)
        if user:
            user_menu_order = user.get('menu_order')
    if request.method == 'POST':
        new_order = request.form.getlist('menu_order[]')
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                try:
                    users = json.load(f)
                except Exception:
                    users = []
        else:
            users = []
        for u in users:
            if u.get('username') == username:
                u['menu_order'] = new_order
        with open(user_file, 'w') as f:
            json.dump(users, f, indent=4)
        flash('Menu order saved!', 'success')
        user_menu_order = new_order
    menu_options = user_menu_order if user_menu_order else all_menu_options
    return render_template('customization.html', menu_options=menu_options, role=role)

@app.route('/templates', methods=['GET'])
def templates_page():
    return render_template('templates.html', role=request.cookies.get('role', ''))

# Edit template (GET shows form, POST saves changes)
@app.route('/edit_template/<template_name>', methods=['GET', 'POST'])
def edit_template(template_name):
    templates_dir = os.path.join(db_folder, 'templates')
    template_path = os.path.join(templates_dir, template_name)
    if not os.path.exists(template_path):
        return f"Template '{template_name}' not found.", 404
    if request.method == 'POST':
        new_content = request.form.get('template_content', '')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        flash('Template updated successfully.', 'success')
        return redirect(url_for('templates_page'))
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return render_template('edit_template.html', template_name=template_name, template_content=content, role=request.cookies.get('role', ''))
@app.route('/delete_job/<job_id>', methods=['POST', 'GET'])
def delete_job(job_id):
    # Load jobs
    jobs = []
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            try:
                jobs = json.load(f)
            except Exception:
                jobs = []
    # Remove job (compare as string)
    jobs = [j for j in jobs if str(j.get('job_id')) != str(job_id)]
    # Save jobs
    with open(jobs_file, 'w') as f:
        json.dump(jobs, f, indent=2)
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('jobs_list'))

@app.route('/edit_job/<job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    # Load jobs
    jobs = []
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            try:
                jobs = json.load(f)
            except Exception:
                jobs = []
    # Find job (compare as string)
    job = next((j for j in jobs if str(j.get('job_id')) == str(job_id)), None)
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('jobs_list'))
    if request.method == 'POST':
        job['job_title'] = request.form.get('job_title', job['job_title'])
        job['job_description'] = request.form.get('job_description', job['job_description'])
        job['job_location'] = request.form.get('job_location', job['job_location'])
        job['job_type'] = request.form.get('job_type', job['job_type'])
        job['job_requirements'] = request.form.get('job_requirements', job['job_requirements'])
        # Save jobs
        with open(jobs_file, 'w') as f:
            json.dump(jobs, f, indent=2)
        flash('Job updated successfully.', 'success')
        return redirect(url_for('jobs_list'))
    return render_template('edit_job.html', job=job)







@app.route('/')
def index():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    # --- Key Metrics for Dashboard ---
    # Total Applicants: count of all candidates
    candidates = []
    candidates_file = os.path.join(db_folder, 'candidates.json')
    if os.path.exists(candidates_file):
        with open(candidates_file, 'r') as f:
            try:
                candidates = json.load(f)
            except Exception:
                candidates = []
    total_applicants = len(candidates)
    total_hired = sum(1 for c in candidates if c.get('status', '').lower() == 'hired')
    # Attrition Score: percent of hired who are no longer with company (status = 'Resigned' or 'Fired')
    total_left = sum(1 for c in candidates if c.get('status', '').lower() in ['resigned', 'fired'])
    attrition_score = 0
    if total_hired > 0:
        attrition_score = round((total_left / total_hired) * 100, 1)
    # Pass to template
    logged_in_cookie = request.cookies.get('logged_in')
    is_logged_in = logged_in_cookie == 'true'
    role = request.cookies.get('role', '') if is_logged_in else ''
    username = request.cookies.get('username', '') if is_logged_in else ''
    email = request.cookies.get('email', '') if is_logged_in else ''
    phone = request.cookies.get('phone', '') if is_logged_in else ''
    department = request.cookies.get('department', '') if is_logged_in else ''
    time = datetime.datetime.now().strftime("%H:%M:%S")
    greeting = "Good Morning" if int(time.split(':')[0]) < 12 else "Good Afternoon" if int(time.split(':')[0]) < 18 else "Good Evening"
    access_control = []
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    user_file = os.path.join(db_folder, 'userdata.json')
    # Load users only once
    users = []
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = []
    user = next((u for u in users if u['username'] == username), None)
    if user:
        access_control = user.get('access_control', [])

    # Calculate candidates_managed_count and pending_approvals efficiently
    candidates_list = fetch_candidate_data()
    candidates_managed_count = len(candidates_list)
    pending_approvals = fetch_pending_approvals()
    pending_approvals_count = len(pending_approvals)

    # --- Add line chart data for dashboard (real-time, consistent with milestone) ---
    import json as pyjson
    import calendar
    from collections import defaultdict
    def group_by_period(items, date_key, period):
        grouped = defaultdict(int)
        labels = []
        now = datetime.datetime.now()
        if period == 'month':
            for i in range(5, -1, -1):
                dt = (now - datetime.timedelta(days=30*i)).replace(day=1)
                label = dt.strftime('%b %Y')
                labels.append(label)
                grouped[label] = 0
            for item in items:
                date_str = item.get(date_key)
                try:
                    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    label = dt.strftime('%b %Y')
                    if label in grouped:
                        grouped[label] += 1
                except Exception:
                    continue
        elif period == 'week':
            for i in range(5, -1, -1):
                start = now - datetime.timedelta(days=now.weekday() + 7*i)
                label = f"Week {start.isocalendar()[1]} {start.year}"
                labels.append(label)
                grouped[label] = 0
            for item in items:
                date_str = item.get(date_key)
                try:
                    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    label = f"Week {dt.isocalendar()[1]} {dt.year}"
                    if label in grouped:
                        grouped[label] += 1
                except Exception:
                    continue
        elif period == 'day':
            for i in range(6, -1, -1):
                dt = now - datetime.timedelta(days=i)
                label = dt.strftime('%Y-%m-%d')
                labels.append(label)
                grouped[label] = 0
            for item in items:
                date_str = item.get(date_key)
                try:
                    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    label = dt.strftime('%Y-%m-%d')
                    if label in grouped:
                        grouped[label] += 1
                except Exception:
                    continue
        return labels, [grouped[l] for l in labels]

    jobs = []
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            try:
                jobs = json.load(f)
            except Exception:
                jobs = []
    job_items = []
    for job in jobs:
        posted_at = job.get('posted_at', '')
        if posted_at:
            try:
                date_str = posted_at.split(' ')[0]
                job_items.append({'date': date_str})
            except Exception:
                continue
    hired_candidates = [c for c in candidates if c.get('status', '').lower() == 'hired']
    hired_items = []
    for c in hired_candidates:
        applied_date = c.get('applied_date', '')
        if applied_date:
            hired_items.append({'date': applied_date})

    vacancy_hired_labels = {}
    total_vacancies_data = {}
    total_hired_data = {}
    for period in ['month', 'week', 'day']:
        labels, vacancies = group_by_period(job_items, 'date', period)
        _, hired = group_by_period(hired_items, 'date', period)
        vacancy_hired_labels[period] = labels
        total_vacancies_data[period] = vacancies
        total_hired_data[period] = hired
    vacancy_hired_labels_json = pyjson.dumps(vacancy_hired_labels)
    total_vacancies_data_json = pyjson.dumps(total_vacancies_data)
    total_hired_data_json = pyjson.dumps(total_hired_data)

    # --- Candidate Spotlight Logic REMOVED ---
    # (Removed to prevent unnecessary API calls and errors)

    notification_file = os.path.join(db_folder, 'notifications.json')
    all_notifications = []
    if os.path.exists(notification_file):
        with open(notification_file, 'r') as nf:
            try:
                all_notifications = json.load(nf)
            except json.JSONDecodeError:
                all_notifications = []
    user_notifications = [n for n in all_notifications if n.get('for_role') == role]


    # Use DB scan for upcoming interviews (and optionally other events)
    from data import fetch_all_upcoming_events, fetch_recent_activities
    all_upcoming = fetch_all_upcoming_events(limit=30)
    all_events = [e for e in all_upcoming if e.get('type') == 'Interview']
    recent_activities = fetch_recent_activities()

    # No AI insights, only upcoming interviews and pending approvals will be shown in dashboard card.
    # Prepare radar chart data for five candidate metrics
    radar_labels = ['Active Applicants', 'Shortlisted', 'Interviewed', 'Ready to Hire', 'Hired']
    radar_data = [
        len(candidates_list),
        sum(1 for c in candidates_list if c.get('status') == 'Shortlisted'),
        sum(1 for c in candidates_list if c.get('status') == 'Interviewed'),
        sum(1 for c in candidates_list if c.get('status') == 'Approved'),
        sum(1 for c in candidates_list if c.get('status') == 'Hired')
    ]
    import json as pyjson
    radar_labels_json = pyjson.dumps(radar_labels)
    radar_data_json = pyjson.dumps(radar_data)
    # Always load dashboard data, but show login if not logged in
    if is_logged_in:
        return render_template('dashboard.html',
                               logged_in=True,
                               username=username,
                               email=email,
                               phone=phone,
                               department=department,
                               role=role,
                               access_control=access_control,
                               is_logged_in=is_logged_in,
                               greeting=greeting,
                               job_count=job_count(),
                               openings=openings_count(),
                               users=fetch_user_data(),
                               user_count=total_users(),
                               candidate_count=candidate_count(),
                               candidates_list=candidates_list,
                               candidates_managed_count=candidates_managed_count,
                               notifications=user_notifications, 
                               pending_approvals=pending_approvals,
                               pending_approvals_count=pending_approvals_count,
                               all_events=all_events,
                               recent_activities=recent_activities,
                               radar_labels_json=radar_labels_json,
                               radar_data_json=radar_data_json,
                               vacancy_hired_labels_json=vacancy_hired_labels_json,
                               total_vacancies_data_json=total_vacancies_data_json,
                               total_hired_data_json=total_hired_data_json,
                               total_applicants=total_applicants,
                               total_hired=total_hired,
                               attrition_score=attrition_score
                               
                               )
    else:
        # Show dashboard with default/empty values for not logged in
        return render_template('dashboard.html',
                               logged_in=False,
                               username='',
                               email='',
                               phone='',
                               department='',
                               role='',
                               access_control=[],
                               is_logged_in=False,
                               greeting=greeting,
                               job_count=job_count(),
                               openings=openings_count(),
                               users=fetch_user_data(),
                               user_count=total_users(),
                               candidate_count=candidate_count(),
                               candidates_list=[],
                               candidates_managed_count=0,
                               notifications=[], 
                               pending_approvals=[],
                               pending_approvals_count=0,
                               all_events=[],
                               recent_activities=[],
                               radar_labels_json=radar_labels_json,
                               radar_data_json=radar_data_json,
                               vacancy_hired_labels_json=vacancy_hired_labels_json,
                               total_vacancies_data_json=total_vacancies_data_json,
                               total_hired_data_json=total_hired_data_json,
                               system_ai_insight=None
                               )
# Regenerate System Insights API
@app.route('/regenerate_system_insights', methods=['POST'])
def regenerate_system_insights():
    """
    Regenerates the system-wide AI insights and returns them as JSON.
    """
    try:
        from Aion import chat_with_bot, SYSTEM_PROMPT
        from data import fetch_all_db_data
        cache = {}
        all_data = fetch_all_db_data()
        user_input = (
            "Using only the following internal data from our system, provide 3 concise, actionable insights that analyze: "
            "1. Candidate performance trends and analytics (e.g., strengths, weaknesses, hiring outcomes, probation results). "
            "2. Job posting effectiveness and analytics (e.g., which postings attract the best candidates, match rates, bottlenecks). "
            "3. Process flow and system-wide analytics (e.g., approval cycles, onboarding, areas for improvement in our workflow). "
            "Do not reference external platforms, generic advice, or invent information. Only use the data provided. "
            "Use bullet points. Data: " + json.dumps(all_data, ensure_ascii=False)
        )
        insight = chat_with_bot(user_input, system_prompt=SYSTEM_PROMPT)
        cache['system_ai_insight'] = markdown.markdown(insight)
        # Optionally update dashboard_ai_cache.json
        cache_file = os.path.join(os.path.dirname(__file__), 'db', 'dashboard_ai_cache.json')
        try:
            with open(cache_file, 'r') as f:
                old_cache = json.load(f)
        except Exception:
            old_cache = {}
        old_cache['system_ai_insight'] = cache['system_ai_insight']
        with open(cache_file, 'w') as f:
            json.dump(old_cache, f, indent=2)
        return jsonify({'success': True, 'system_ai_insight': cache['system_ai_insight']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    user_file = os.path.join(db_folder, 'userdata.json')
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = []
    else:
        users = []
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    if user:
        from flask import make_response
        response = make_response(render_template('dashboard.html',
            logged_in=True,
            username=user['username'],
            email=user.get('email', ''),
            phone=user.get('phone', ''),
            department=user.get('department', ''),
            role=user.get('role', ''),
            access_control=user.get('access_control', []),
            is_logged_in=True
        ))
        response.set_cookie('logged_in', 'true', httponly=True, secure=False)
        response.set_cookie('username', user['username'], httponly=True, secure=False)
        response.set_cookie('email', user.get('email', ''), httponly=True, secure=False)
        response.set_cookie('phone', user.get('phone', ''), httponly=True, secure=False)
        response.set_cookie('session', 'active', httponly=True, secure=False)
        response.set_cookie('department', user.get('department', ''), httponly=True, secure=False)
        response.set_cookie('role', user.get('role', ''), httponly=True, secure=False)
        return response
    else:
        return render_template('login.html', error='Invalid username or password'), 401
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    response = jsonify({'message': 'Logout successful'})
    response.set_cookie('logged_in', 'false', httponly=True, secure=False)
    return render_template('login.html', logged_in=False)
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    phone = request.form.get('phone')
    department = request.form.get('department')
    role = request.form.get('role')

    if username and password and email and phone:
        departments_list = [
            'Process and HSE',
            'Piping & Mechanical',
            'Civil & Structural',
            'Electrical',
            'Instrumentation and Control',
            'Digitization',
            'AI Development'
        ]
        access_control_map = {
            'Discipline Manager': ["approve_candidates"],
            'Department Manager (MOE)': ["approve_candidates"],
            'Department Manager (MOP)': ["approve_candidates"],
            'Operation Manager': ["approve_candidates"],
            'CEO': ["approve_candidates"]
        }
        access_control = access_control_map.get(role, [])
        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'phone': phone,
            'department': department,
            'role': role,
            'access_control': access_control
        }
        db_folder = os.path.join(os.path.dirname(__file__), 'db')
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
        user_file = os.path.join(db_folder, 'userdata.json')
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                try:
                    users = json.load(f)
                except json.JSONDecodeError:
                    users = []
        else:
            users = []
        users.append(user_data)
        with open(user_file, 'w') as f:
            json.dump(users, f, indent=4)
        response = jsonify({'message': 'Signup successful'})
        response.set_cookie('logged_in', 'true', httponly=True, secure=False)
        response.set_cookie('username', username, httponly=True, secure=False)
        response.set_cookie('email', email, httponly=True, secure=False)
        response.set_cookie('phone', phone, httponly=True, secure=False)
        response.set_cookie('session', 'active', httponly=True, secure=False)
        response.set_cookie('role', role, httponly=True, secure=False)
        response.set_cookie('department', department, httponly=True, secure=False)
        return render_template('dashboard.html',logged_in=True,username=username,email=email,phone=phone,department=department,role=role,access_control=access_control)
    else:
        return render_template('signup.html', error='All fields are required', departments_list=[
            'Process and HSE',
            'Piping & Mechanical',
            'Civil & Structural',
            'Electrical',
            'Instrumentation and Control',
            'Digitization',
            'AI Development'
        ]), 400

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/jobs_list')
def jobs_list():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    job_file = os.path.join(db_folder, 'jobs.json')
    jobs = []
    view = request.args.get('view', 'table').lower()
    if view not in ('table', 'card'):
        view = 'table'
    if os.path.exists(job_file):
        with open(job_file, 'r') as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    return render_template('jobs_list.html', jobs=jobs ,role=request.cookies.get('role', '') ,view=view)

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/post_jobs', methods=['POST', 'GET'])
def post_jobs():
    logged_in_cookie = request.cookies.get('logged_in')
    is_logged_in = logged_in_cookie == 'true'
    if not is_logged_in:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Load jobs and determine next job_id
        db_folder = os.path.join(os.path.dirname(__file__), 'db')
        job_file = os.path.join(db_folder, 'jobs.json')
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                try:
                    jobs = json.load(f)
                except json.JSONDecodeError:
                    jobs = []
        else:
            jobs = []
        # Find max job_id (skip nulls and non-integer ids)
        max_id = 0
        for job in jobs:
            try:
                jid = int(job.get('job_id', 0))
                if jid > max_id:
                    max_id = jid
            except (TypeError, ValueError):
                continue
        job_id = str(max_id + 1)

        job_title = request.form.get('job_title', '').strip()
        job_location = request.form.get('job_location', '').strip()
        job_type = request.form.get('job_type', '').strip()
        job_openings = request.form.get('job_openings', '').strip()
        job_posted_by = request.cookies.get('username', '').strip()
        job_lead_time = request.form.get('lead_time', '').strip()
        job_requirements = request.form.get('job_requirements', '').strip()
        department = request.form.get('department', '').strip()
        seniority_level = request.form.get('seniority_level', '').strip()
        salary_range = request.form.get('salary_range', '').strip()
        jd_option = request.form.get('jd_option', '').strip()
        job_description = ""
        jd_file_path = ""
        # Validate all required fields
        required_fields = [job_title, job_location, job_type, job_openings, job_posted_by, job_lead_time, job_requirements, department, seniority_level, salary_range]
        if not all(required_fields):
            flash('All fields are required. Please fill in all details.', 'error')
            return redirect(request.url)
        # Handle JD upload or creation
        if 'jd_file' in request.files:
            jd_file = request.files['jd_file']
            if jd_file and jd_file.filename:
                upload_folder = os.path.join(db_folder, 'uploads', 'jd_files')
                os.makedirs(upload_folder, exist_ok=True)
                ext = os.path.splitext(jd_file.filename)[1]
                # Use timestamp for uniqueness
                import time
                timestamp = int(time.time())
                jd_filename = secure_filename(f"jd_{job_id}_{timestamp}{ext}")
                # Always use forward slashes for Flask static serving
                jd_file_path = f"uploads/jd_files/{jd_filename}".replace('\\', '/')
                abs_jd_file_path = os.path.join(db_folder, 'uploads', 'jd_files', jd_filename)
                jd_file.save(abs_jd_file_path)
                # Extract JD text using AI
                from data import extract_text_from_file, extract_jd_with_openai
                jd_text = extract_text_from_file(abs_jd_file_path)
                job_description = extract_jd_with_openai(jd_text)
            else:
                flash('JD file is required. Please upload a valid file.', 'error')
                return redirect(request.url)
        elif jd_option == "create":
            job_description = request.form.get('job_description', '')
            jd_file_path = ""  # No file uploaded
        else:
            job_description = ""
            jd_file_path = ""  # No file uploaded
        job_data = {
            'job_id': job_id,
            'job_title': job_title,
            'job_description': job_description,
            'job_location': job_location,
            'job_type': job_type,
            'job_requirements': job_requirements,
            'job_openings': job_openings,
            'job_posted_by': job_posted_by,
            'job_lead_time': job_lead_time,
            'department': department,
            'seniority_level': seniority_level,
            'salary_range': salary_range,
            'jd_file_path': jd_file_path,
            'posted_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        jobs.append(job_data)
        with open(job_file, 'w') as f:
            json.dump(jobs, f, indent=4)
        return redirect(url_for('jobs_list'))
    return render_template('post_jobs.html', is_logged_in=is_logged_in , role=request.cookies.get('role', ''))

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_candidates')
def manage_candidates():
    candidates_list = fetch_candidate_data()
    # Show onboarding status for hired candidates
    for candidate in candidates_list:
        if candidate.get('status') == 'Hired' and 'onboarding' in candidate:
            candidate['onboarding_progress'] = sum(1 for v in candidate['onboarding'].values() if v == 'Completed')
            candidate['onboarding_total'] = len(candidate['onboarding'])
    view = request.args.get('view', 'table')
    return render_template('manage_candidates.html', role=request.cookies.get('role', ''), candidates_list=candidates_list, view=view)

    # removed duplicate import of threading

def generate_probation_insights_async(candidate_id, pa, candidate_file):
    import hashlib, json, markdown
    try:
        # Load candidates from file
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except Exception:
                    candidates = []
        else:
            candidates = []
        candidate = next((c for c in candidates if c.get('id') == candidate_id), None)
        if not candidate:
            return
        if 'probation_assessment_insights' not in candidate or not isinstance(candidate['probation_assessment_insights'], dict):
            candidate['probation_assessment_insights'] = {}
        updated = False
        for month in range(1, 7):
            month_str = str(month)
            if pa.get(month_str):
                pa_month = pa[month_str]
                pa_month_hash = hashlib.md5(json.dumps(pa_month, sort_keys=True).encode()).hexdigest()
                insight_key = f'_pa_hash_{month_str}'
                # Only update if hash is missing or changed, or summary is missing
                if (
                    not candidate.get(insight_key)
                    or candidate.get(insight_key) != pa_month_hash
                    or not candidate['probation_assessment_insights'].get(month_str)
                ):
                    user_input = f"Summarize the following probation assessment data for month {month}. Only use the information provided. Do not invent or assume anything. Be concise and factual.\nAssessment Data: {json.dumps(pa_month, ensure_ascii=False)}"
                    from Aion import chat_with_bot, SYSTEM_PROMPT
                    insight = chat_with_bot(user_input, system_prompt=SYSTEM_PROMPT)
                    try:
                        insight_html = markdown.markdown(insight)
                    except Exception:
                        insight_html = insight
                    candidate['probation_assessment_insights'][month_str] = insight_html
                    candidate[insight_key] = pa_month_hash
                    updated = True
        if updated:
            with open(candidate_file, 'w') as f:
                json.dump(candidates, f, indent=4)
    except Exception as e:
        pass
    show_send_for_approval = False
    show_negotiation_mail = False
    show_approve_button = False
    show_offer_letter = False
    # Determine which form to show based on status
    role = request.cookies.get('role', '')
    if candidate:
        status = candidate.get('status', '')
        if status == 'Shortlisted':
            show_interview_form = True
        elif status == 'Interview Scheduled':
            show_video_upload = True
        elif status == 'Interview Analyzed':
            if role == 'HR':
                show_send_for_approval = True
        elif status == 'Pending Approval':
            if role == 'HR Manager':
                show_negotiation_mail = True
                show_approve_button = True
        elif status == 'On Hold':
            if role == 'HR Manager':
                show_approve_button = True
        elif status == 'Rejected':
            pass
        elif status == 'Approved':
            if role == 'Manager':
                show_offer_letter = True
        # Add more status-based logic as needed
        # Fetch notifications for the user
        notification_file = os.path.join(os.path.dirname(__file__), 'db', 'notifications.json')
        if os.path.exists(notification_file):
            with open(notification_file, 'r') as nf:
                try:
                    notifications = json.load(nf)
                except json.JSONDecodeError:
                    notifications = []
        else:
            notifications = []
        user_notifications = [n for n in notifications if n.get('candidate_id') == candidate_id and n.get('for_role') == role]
        return render_template('candidate_profile.html', candidate=candidate, role=role,
                              schedule_interview=schedule_interview,
                              show_interview_form=show_interview_form,
                              show_video_upload=show_video_upload,
                              show_send_for_approval=show_send_for_approval,
                              show_negotiation_mail=show_negotiation_mail,
                              show_approve_button=show_approve_button,
                              show_offer_letter=show_offer_letter,
                              interviewer=get_sender(),
                              notifications=user_notifications)
    else:
        return "Candidate not found", 404
    
@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'resume' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    resume = request.files['resume']
    if resume.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    resume_folder = os.path.join(db_folder, 'resumes')
    os.makedirs(resume_folder, exist_ok=True)
    from werkzeug.utils import secure_filename
    import time
    ext = os.path.splitext(resume.filename)[1]
    timestamp = int(time.time())
    resume_filename = secure_filename(f"cv_{timestamp}{ext}")
    # Always use forward slashes for Flask static serving
    resume_path = f"resumes/{resume_filename}".replace('\\', '/')
    abs_resume_path = os.path.join(db_folder, 'resumes', resume_filename)
    resume.save(abs_resume_path)
    row_candidate_data = extract_resume_with_openai(abs_resume_path)
    # Debug: print the extracted data to server log
    print('Extracted candidate data:', row_candidate_data, file=sys.stderr)
    # Handle extraction errors
    if isinstance(row_candidate_data, dict) and 'error' in row_candidate_data:
        print('Resume extraction error:', row_candidate_data['error'], file=sys.stderr)
        return jsonify({'message': f"Resume extraction failed: {row_candidate_data['error']}"}), 400
    if isinstance(row_candidate_data, str):
        # Remove Markdown code block markers if present
        row_candidate_data = row_candidate_data.strip()
        if row_candidate_data.startswith("```"):
            row_candidate_data = row_candidate_data.strip("`")
            row_candidate_data = row_candidate_data.lstrip("json").strip()
        try:
            row_candidate_data = json.loads(row_candidate_data)
        except json.JSONDecodeError:
            print('Failed to parse extracted resume data', file=sys.stderr)
            return jsonify({'message': 'Failed to parse extracted resume data'}), 500
    elif not isinstance(row_candidate_data, dict):
        print('Unexpected data format from resume extraction', file=sys.stderr)
        return jsonify({'message': 'Unexpected data format from resume extraction'}), 500
    # Map to consistent fields for your app
    candidate_data = {
        'id': None,  # will set below
        'name': row_candidate_data.get('name', ''),
        'email': row_candidate_data.get('email', ''),
        'phone': row_candidate_data.get('phone', ''),
        'position': row_candidate_data.get('position', row_candidate_data.get('job_title', '')),
        'status': 'New',  # Always set status as New on upload
        'resume_link': row_candidate_data.get('resume_link', ''),
        'cv_path': resume_path,  # always save the uploaded file path
        'applied_date': row_candidate_data.get('applied_date', datetime.datetime.now().strftime('%Y-%m-%d')),
        'notes': row_candidate_data.get('notes', ''),
        'skills': row_candidate_data.get('skills', []),
        'experience': row_candidate_data.get('experience', []),
        'education': row_candidate_data.get('education', []),
        'certifications': row_candidate_data.get('certifications', []),
        'projects': row_candidate_data.get('projects', []),
        'linkedin': row_candidate_data.get('linkedin', ''),
        'github': row_candidate_data.get('github', '')
    }
    # Get job_id from form
    job_id = request.form.get('job_id')
    # Get minimum match score from job data
    min_match_score = 0
    job_file = os.path.join(db_folder, 'jobs.json')
    job_data = None
    if job_id and os.path.exists(job_file):
        with open(job_file, 'r') as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
        for job in jobs:
            if str(job.get('job_id')) == str(job_id):
                job_data = job
                break
        if job_data:
            min_match_score = int(job_data.get('min_match_score', 0)) if job_data.get('min_match_score') else 0
            # Use JD file text if available, else job_description + requirements
            jd_file_path = job_data.get('jd_file_path', '')
            jd_text = ''
            if jd_file_path:
                abs_jd_file_path = os.path.join(db_folder, jd_file_path)
                if os.path.exists(abs_jd_file_path):
                    from data import extract_text_from_file
                    jd_text = extract_text_from_file(abs_jd_file_path)
            if not jd_text:
                jd_text = (job_data.get('job_description', '') or '') + ' ' + (job_data.get('job_requirements', '') or '')
            from data import analyze_cv_with_jd
            match_score = analyze_cv_with_jd(row_candidate_data, jd_text)
            candidate_data['match_score'] = match_score
        else:
            candidate_data['match_score'] = 0
    else:
        candidate_data['match_score'] = 0
    # Save candidate to global candidates.json
    candidate_file = os.path.join(db_folder, 'candidates.json')
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidates = json.load(f)
            except json.JSONDecodeError:
                candidates = []
    else:
        candidates = []
    candidate_data['id'] = len(candidates) + 1
    candidate_data['job_id'] = str(job_id) if job_id is not None else None
    candidates.append(candidate_data)
    with open(candidate_file, 'w') as f:
        json.dump(candidates, f, indent=4)
    # Save candidate to job-specific file for job details page
    if job_id is not None:
        job_cv_file = os.path.join(db_folder, f'job_{job_id}_cvs.json')
        if os.path.exists(job_cv_file):
            with open(job_cv_file, 'r') as f:
                try:
                    job_cvs = json.load(f)
                except json.JSONDecodeError:
                    job_cvs = []
        else:
            job_cvs = []
        # Prepare minimal CV info for job details page
        job_cv_info = {
            'candidate_id': candidate_data['id'],
            'candidate_name': candidate_data.get('name', ''),
            'candidate_email': candidate_data.get('email', ''),
            'cv_link': resume_path  # relative path for url_for
        }
        job_cvs.append(job_cv_info)
        with open(job_cv_file, 'w') as f:
            json.dump(job_cvs, f, indent=4)
    # Redirect to manage_candidates so the list is always refreshed
    return redirect(url_for('manage_candidates'))



@app.route('/schedule_interview', methods=['POST'])
def schedule_interview():
    """
    Schedules an interview for a candidate based on the provided candidate_id and interview details.
    Accepts both JSON and form data.
    """
    try:
        if request.is_json:
            data = request.get_json()
            candidate_id = data.get('candidate_id')
            interview_date = data.get('interview_date')
            interview_time = data.get('interview_time')
            intervier = data.get('intervier')
        else:
            candidate_id = request.form.get('candidate_id')
            interview_date = request.form.get('interview_date')
            interview_time = request.form.get('interview_time')
            # Get interviewer from form, fallback to username from cookies
            intervier = request.form.get('interviewer') or request.cookies.get('username', '')
            
        if not candidate_id or not interview_date or not interview_time or not intervier:
            return jsonify({'success': False, 'message': 'Missing candidate ID or interview details'}), 400
        try:
            candidate_id = int(candidate_id)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid candidate ID format'}), 400
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []
        for c in candidates:
            if c.get('id') == candidate_id:
                c['interview_date'] = interview_date
                c['interview_time'] = interview_time
                c['intervier'] = intervier
                c['status'] = 'Interview Scheduled'
                break
        else:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        # Redirect to the candidate's profile page after scheduling the interview
        return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', ''), schedule_interview=True))
    except Exception as e:
        print(f"[ERROR] Failed to schedule interview: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    



@app.route('/interview_analysis', methods=['POST'])
def interview_analysis():
    """
    Accepts a video file and candidate_id, performs audio extraction, transcription, and AI analysis.
    Returns JSON with analysis results and score.
    """
    try:
        candidate_id = request.form.get('candidate_id', type=int)
        video_file = request.files.get('video_file')
        if not candidate_id or not video_file or video_file.filename == '':
            return jsonify({'success': False, 'message': 'Missing candidate ID or video file'}), 400

        # Validate file type
        allowed_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv'}
        ext = os.path.splitext(video_file.filename)[-1].lower()
        if ext not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Invalid file type.'}), 400

        # Validate file size (500MB)
        video_file.seek(0, 2)
        file_size = video_file.tell()
        video_file.seek(0)
        if file_size > 500 * 1024 * 1024:
            return jsonify({'success': False, 'message': 'File size must be less than 500MB'}), 400

        # Save video
        video_dir = os.path.join(app.root_path, 'uploads', 'interview_videos')
        os.makedirs(video_dir, exist_ok=True)
        from werkzeug.utils import secure_filename
        safe_filename = secure_filename(f"interview_{candidate_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
        video_path = os.path.join(video_dir, safe_filename)
        video_file.save(video_path)

        # Extract audio
        audio_path = os.path.splitext(video_path)[0] + ".wav"
        ok = extract_audio_from_video(video_path, audio_path)
        if not ok:
            return jsonify({'success': False, 'message': 'Audio extraction failed'}), 500

        # Transcribe
        transcript = transcribe_with_whisper(audio_path)
        if not transcript:
            return jsonify({'success': False, 'message': 'Transcription failed'}), 500

        # Analyze with AI
        summary = analyze_transcript_with_openai(transcript)
        score = extract_score_from_summary(summary)

        # Update candidate profile with analysis results
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []

        for c in candidates:
            if c.get('id') == candidate_id:
                c['interview_transcript'] = transcript
                c['ai_interview_report'] = summary
                c['interview_score'] = score
                c['status'] = 'Interview Analyzed'
                break

        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)

        return jsonify({
            'success': True,
            'transcript': transcript,
            'ai_report': summary,
            'score': score
        })
    except Exception as e:
        print(f"[ERROR] Interview analysis failed: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/update_candidate_status', methods=['POST'])
def update_candidate_status():
    """
    Updates the status of a candidate based on the provided candidate_id and new status.
    Accepts both JSON and form data.
    """
    try:
        # Always define these variables
        schedule_interview = False
        selected_candidate = False
        if request.is_json:
            data = request.get_json()
            candidate_id = data.get('candidate_id')
            new_status = data.get('new_status')
            if new_status == "Shortlisted":
                schedule_interview = True
            if new_status == "Selected":
                selected_candidate = True
        else:
            candidate_id = request.form.get('candidate_id')
            new_status = request.form.get('new_status')
            if new_status == "Shortlisted":
                schedule_interview = True
            if new_status == "Selected":
                selected_candidate = True
        if not candidate_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing candidate ID or new status'}), 400
        try:
            candidate_id = int(candidate_id)
        except Exception:
            pass
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []
        candidate = None
        for c in candidates:
            if c.get('id') == candidate_id:
                c['status'] = new_status
                candidate = c
                break
        else:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        # If status is Shortlisted, reload candidate and show interview form
        if new_status == "Shortlisted":
            return render_template('candidate_profile.html', candidate=candidate, role=request.cookies.get('role', ''), schedule_interview=True, selected_candidate=selected_candidate)
        # Otherwise, redirect as before
        return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', ''), schedule_interview=schedule_interview , selected_candidate=selected_candidate ))
    except Exception as e:
        print(f"[ERROR] Failed to update candidate status: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ---------------------------------------------------------------------------------------------------------------------
@app.route('/send_for_approval', methods=['POST'])
def send_for_approval():
    """
    Sends a candidate for approval based on the provided candidate_id.
    Accepts form data.
    """
    try:
        candidate_id = request.form.get('candidate_id')
        if not candidate_id:
            return jsonify({'success': False, 'message': 'Missing candidate ID'}), 400
        try:
            candidate_id = int(candidate_id)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid candidate ID format'}), 400
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []
        updated = False
        for c in candidates:
            if c.get('id') == candidate_id:
                c['status'] = 'Pending Approval'
                updated = True
                break
        if not updated:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        # After updating, reload candidate data for the profile page
        candidates_list = fetch_candidate_data()
        candidate = next((c for c in candidates_list if c.get('id') == candidate_id), None)
        return render_template('candidate_profile.html', candidate=candidate, role=request.cookies.get('role', ''), schedule_interview=False)
    except Exception as e:
        print(f"[ERROR] Failed to send candidate for approval: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/approve_candidate', methods=['POST'])
def approve_candidate():
    """
    Approves a candidate (HR Manager or Manager action).
    Sets status to 'Approved'.
    """
    try:
        candidate_id = request.form.get('candidate_id')
        approval_comment = request.form.get('approval_comment', '')
        if not candidate_id:
            return jsonify({'success': False, 'message': 'Missing candidate ID'}), 400
        candidate_id = int(candidate_id)
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []
        updated = False
        for c in candidates:
            if c.get('id') == candidate_id:
                action = request.form.get('action', 'approve')
                if action == 'hold':
                    c['status'] = 'On Hold'
                elif action == 'reject':
                    c['status'] = 'Rejected'
                else:
                    # If approved by Department Manager, set to Pending Offer for Operation Manager
                    if request.cookies.get('role', '') in ['Department Manager (MOE)', 'Department Manager (MOP)']:
                        c['status'] = 'Pending Offer'
                    elif request.cookies.get('role', '') == 'Operation Manager':
                        c['status'] = 'Hired'
                    else:
                        c['status'] = 'Approved'
                c['approval_comment'] = approval_comment
                # Add notification for HR
                notification_file = os.path.join(os.path.dirname(__file__), 'db', 'notifications.json')
                if os.path.exists(notification_file):
                    with open(notification_file, 'r') as nf:
                        try:
                            notifications = json.load(nf)
                        except json.JSONDecodeError:
                            notifications = []
                else:
                    notifications = []
                notifications.append({
                    'candidate_id': candidate_id,
                    'type': 'approval',
                    'status': c['status'],
                    'comment': approval_comment,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'for_role': 'HR'
                })
                with open(notification_file, 'w') as nf:
                    json.dump(notifications, nf, indent=4)
                updated = True
                break
        if not updated:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', '')))
    except Exception as e:
        print(f"[ERROR] Failed to approve candidate: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/recent_activities')
def recent_activities():
    todays_activities = fetch_todays_activities()
    recent_activities = fetch_recent_activities()
    # If the request is from the chatbot (expects JSON), return JSON
    if 'application/json' in request.headers.get('Accept', '') or request.args.get('format') == 'json':
        return jsonify({
            'recent_activities': recent_activities,
            'todays_activities': todays_activities
        })
    # Otherwise, render the template as before
    return render_template(
        'recent_activities.html',
        todays_activities=todays_activities,
        recent_activities=recent_activities,
        role=request.cookies.get('role', '')
    )



# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_hr_team')
def manage_hr_team():
    role = request.cookies.get('role', '')
    if role not in ['HR Manager', 'Manager', 'Admin', 'CEO', 'Operation Manager']:
        msg = "You do not have permission to access this page."
        return render_template('error.html', message=msg, role=role)
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    hr_file = os.path.join(db_folder, 'userdata.json')
    candidate_file = os.path.join(db_folder, 'candidates.json')
    notification_file = os.path.join(db_folder, 'notifications.json')
    jobs_file = os.path.join(db_folder, 'jobs.json')
    # HR team
    if os.path.exists(hr_file):
        with open(hr_file, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = []
        hr_team = [u for u in users if u.get('role') in ['HR', 'HR Manager']]
    else:
        hr_team = []
    # Candidates
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidates = json.load(f)
            except json.JSONDecodeError:
                candidates = []
    else:
        candidates = []
    # Notifications
    if os.path.exists(notification_file):
        with open(notification_file, 'r') as f:
            try:
                notifications = json.load(f)
            except json.JSONDecodeError:
                notifications = []
    else:
        notifications = []
    # Jobs
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    else:
        jobs = []
    # Build approval flows grouped by job
    color_map = {
        'Discipline Manager': '#dc3545',
        'Department Manager': '#fd7e14',
        'Operation Manager': '#28a745',
        'CEO': '#007bff',
        'Approved': '#007bff'
    }
    jobs_with_candidates = []
    for job in jobs:
        job_id = str(job.get('job_id')) if job.get('job_id') is not None else None
        job_candidates = [c for c in candidates if str(c.get('job_id')) == job_id]
        approval_flows = []
        for c in job_candidates:
            flow = {
                'candidate_id': c.get('id'),
                'candidate_name': c.get('name', 'Unknown'),
                'steps': []
            }
            # Determine position for approval cycle
            position = c.get('position', '').lower()
            # If candidate is Hired or Approved, mark all steps as Approved
            if c.get('status') in ['Hired', 'Approved']:
                if 'discipline manager' in position or 'project manager' in position:
                    flow['steps'].append({'role': 'Department Manager (MOE/MOP)', 'action': 'Approved', 'color': color_map['Department Manager']})
                    flow['steps'].append({'role': 'Operation Manager', 'action': 'Approved', 'color': color_map['Operation Manager']})
                    flow['steps'].append({'role': 'CEO', 'action': 'Approved', 'color': color_map['CEO']})
                else:
                    flow['steps'].append({'role': 'Discipline Manager', 'action': 'Approved', 'color': color_map['Discipline Manager']})
                    flow['steps'].append({'role': 'Department Manager (MOE/MOP)', 'action': 'Approved', 'color': color_map['Department Manager']})
                    flow['steps'].append({'role': 'Operation Manager', 'action': 'Approved', 'color': color_map['Operation Manager']})
            else:
                if 'discipline manager' in position or 'project manager' in position:
                    # Step 1: Department Manager (MOE/MOP)
                    dept_manager_action = None
                    for n in notifications:
                        if n.get('candidate_id') == c.get('id') and n.get('for_role') in ['Department Manager (MOE)', 'Department Manager (MOP)']:
                            dept_manager_action = n.get('status', 'Sent')
                    flow['steps'].append({
                        'role': 'Department Manager (MOE/MOP)',
                        'action': dept_manager_action if dept_manager_action else 'Pending',
                        'color': color_map['Department Manager']
                    })
                    # Step 2: Operation Manager
                    op_manager_action = None
                    for n in notifications:
                        if n.get('candidate_id') == c.get('id') and n.get('for_role') == 'Operation Manager':
                                                       op_manager_action = n.get('status', 'Sent')
                    flow['steps'].append({
                        'role': 'Operation Manager',         
                        'action': op_manager_action if op_manager_action else 'Pending',
                        'color': color_map['Operation Manager']
                    })
                    # Step 3: CEO
                    ceo_action = None
                    for n in notifications:
                        if n.get('candidate_id') == c.get('id') and n.get('for_role') == 'CEO':
                            ceo_action = n.get('status', 'Sent')
                    flow['steps'].append({
                        'role': 'CEO',
                        'action': ceo_action if ceo_action else 'Pending',
                        'color': color_map['CEO']
                    })
                else:
                    # Step 1: Discipline Manager
                    disc_manager_action = None
                    for n in notifications:
                        if n.get('candidate_id') == c.get('id') and n.get('for_role') == 'Discipline Manager':
                            disc_manager_action = n.get('status', 'Sent')
                    flow['steps'].append({
                        'role': 'Discipline Manager',
                        'action': disc_manager_action if disc_manager_action else 'Pending',
                        'color': color_map['Discipline Manager']
                    })
                    # Step 2: Department Manager (MOE/MOP)
                    dept_manager_action = None
                    for n in notifications:
                        if n.get('candidate_id') == c.get('id') and n.get('for_role') in ['Department Manager (MOE)', 'Department Manager (MOP)']:
                            dept_manager_action = n.get('status', 'Sent')
                    flow['steps'].append({
                        'role': 'Department Manager (MOE/MOP)',
                        'action': dept_manager_action if dept_manager_action else 'Pending',
                        'color': color_map['Department Manager']
                    })
                    # Step 3: Operation Manager
                    op_manager_action = None
                    for n in notifications:
                        if n.get('candidate_id') == c.get('id') and n.get('for_role') == 'Operation Manager':
                            op_manager_action = n.get('status', 'Sent')
                    flow['steps'].append({
                        'role': 'Operation Manager',
                        'action': op_manager_action if op_manager_action else 'Pending',
                        'color': color_map['Operation Manager']
                    })
            # Step 4: Approved
            approved_action = None
            # If candidate is Hired or Approved, show as Approved
            if c.get('status') in ['Hired', 'Approved']:
                approved_action = 'Approved'
            else:
                for n in notifications:
                    if n.get('candidate_id') == c.get('id') and n.get('status') == 'Approved':
                        approved_action = 'Approved'
            flow['steps'].append({
                'role': 'Approved',
                'action': approved_action if approved_action else 'Pending',
                'color': color_map['Approved']
            })
            approval_flows.append(flow)
        jobs_with_candidates.append({
            'job_id': job.get('job_id'),
            'job_title': job.get('job_title'),
            'approval_flows': approval_flows
        })
    return render_template('manage_hr_team.html', hr_team=hr_team, role=role, jobs_with_candidates=jobs_with_candidates)
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/approve_hiring')
def approve_hiring():
    role = request.cookies.get('role', '')
    # Fetch pending approvals
    pending_approvals = fetch_pending_approvals()
    return render_template('pending_approvals.html', pending_approvals=pending_approvals, role=role)
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_users')
def manage_users():
    return render_template('manage_users.html',role=request.cookies.get('role', ''))
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/view_all_hr')
def view_all_hr():
    return render_template('view_all_hr.html',role=request.cookies.get('role', ''))
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_admins')
def manage_admins():
    return render_template('manage_admins.html',role=request.cookies.get('role', ''))

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/probation_assessment', methods=['GET'])
def probation_assessment():
    candidate_id = request.args.get('candidate_id', type=int)
    role = request.cookies.get('role', '')
    candidate = None
    if candidate_id:
        candidates_list = fetch_candidate_data()
        candidate = next((c for c in candidates_list if c.get('id') == candidate_id), None)
    return render_template('probation_assessment.html', candidate=candidate, role=role)


# ---------------------------------------------------------------------------------------------------------------------
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    return render_template('chatbot_x.html', role=request.cookies.get('role', ''))


# ---------------------------------------------------------------------------------------------------------------------






@app.route('/send_negotiation_mail', methods=['POST'])
def send_negotiation_mail():
    """
    HR Manager sends negotiation mail to candidate (salary, negotiation, etc.).
    Optionally, can approve candidate after negotiation.
    """
    try:
        candidate_id = request.form.get('candidate_id')
        negotiation_message = request.form.get('negotiation_message')
        if not candidate_id:
            return jsonify({'success': False, 'message': 'Missing candidate ID'}), 400
        candidate_id = int(candidate_id)
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []
        for c in candidates:
            if c.get('id') == candidate_id:
                c['negotiation_message'] = negotiation_message
                break
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', '')))
    except Exception as e:
        print(f"[ERROR] Failed to send negotiation mail: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/issue_offer_letter', methods=['POST'])
def issue_offer_letter():
    """
    Manager issues offer letter to candidate and updates status.
    """
    try:
        candidate_id = request.form.get('candidate_id')
        offer_details = request.form.get('offer_details')
        if not candidate_id:
            return jsonify({'success': False, 'message': 'Missing candidate ID'}), 400
        candidate_id = int(candidate_id)
        candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except json.JSONDecodeError:
                    candidates = []
        else:
            candidates = []
        manager_name = request.cookies.get('username', '')
        manager_email = request.cookies.get('email', '')
        for c in candidates:
            if c.get('id') == candidate_id:
                c['offer_letter_details'] = offer_details
                c['offer_issued_by'] = manager_name
                c['offer_issued_by_email'] = manager_email
                c['status'] = 'Hired'
                # Minimal onboarding steps
                c['onboarding'] = {
                    'Joining Formalities': 'Pending',
                    'HR Introduction': 'Pending'
                }
                break
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=4)
        return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', '')))
    except Exception as e:
        print(f"[ERROR] Failed to issue offer letter: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/update_onboarding', methods=['POST'])
def update_onboarding():
    """
    Update onboarding step status for a hired candidate (checkboxes in UI).
    """
    candidate_id = request.form.get('candidate_id')
    if not candidate_id:
        return jsonify({'success': False, 'message': 'Missing candidate ID'}), 400
    candidate_id = int(candidate_id)
    candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidates = json.load(f)
            except json.JSONDecodeError:
                candidates = []
    else:
        candidates = []
    updated = False
    for c in candidates:
        if c.get('id') == candidate_id and c.get('status') == 'Hired':
            # Only keep main onboarding fields
            main_steps = ['Joining Formalities', 'HR Introduction', 'Document Verification', 'System Allocation']
            onboarding = {step: c.get('onboarding', {}).get(step, 'Pending') for step in main_steps}
            # Update from form
            for step in main_steps:
                if request.form.get(step.replace(' ', '_').lower()):
                    onboarding[step] = 'Completed'
                else:
                    onboarding[step] = 'Pending'
            c['onboarding'] = onboarding
            updated = True
            break
    with open(candidate_file, 'w') as f:
        json.dump(candidates, f, indent=4)
    if updated:
        return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', '')))
    else:
        return jsonify({'success': False, 'message': 'Candidate not found or not hired'}), 404



@app.route('/submit_probation_assessment/<int:candidate_id>/<int:month>', methods=['POST'])
def submit_probation_assessment(candidate_id, month):
    """
    Save probation assessment for a candidate for a given month (1-6).
    Month 1: cultural fit, loyalty, etc.
    Months 2-6: standard performance criteria.
    """
    candidate_file = os.path.join(os.path.dirname(__file__), 'db', 'candidates.json')
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidates = json.load(f)
            except json.JSONDecodeError:
                candidates = []
    else:
        candidates = []
    candidate = next((c for c in candidates if c.get('id') == candidate_id), None)
    if not candidate:
        return jsonify({'success': False, 'message': 'Candidate not found'}), 404
    # Ensure probation_assessment exists
    if 'probation_assessment' not in candidate:
        candidate['probation_assessment'] = {}
    assessment = {}
    if month == 1:
        assessment['cultural_acceptance'] = request.form.get('cultural_acceptance', '')
        assessment['loyalty'] = request.form.get('loyalty', '')
        assessment['teamwork'] = request.form.get('teamwork', '')
        assessment['adaptability'] = request.form.get('adaptability', '')
        assessment['comments'] = request.form.get('comments', '')
        assessment['assessed_by'] = request.cookies.get('username', '')
        assessment['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    elif 2 <= month <= 6:
        assessment['performance'] = request.form.get('performance', '')
        assessment['attendance'] = request.form.get('attendance', '')
        assessment['initiative'] = request.form.get('initiative', '')
        assessment['communication'] = request.form.get('communication', '')
        assessment['comments'] = request.form.get('comments', '')
        assessment['assessed_by'] = request.cookies.get('username', '')
        assessment['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        return jsonify({'success': False, 'message': 'Invalid month'}), 400
    candidate['probation_assessment'][str(month)] = assessment
    # Save
    for idx, c in enumerate(candidates):
        if c.get('id') == candidate_id:
            candidates[idx] = candidate
            break
    with open(candidate_file, 'w') as f:
        json.dump(candidates, f, indent=4)

    # Background: Generate AI summary if assessment changed
    # removed duplicate import of threading
    def bg_generate_probation_insight(candidate_id, month, assessment, candidate_file):
        import hashlib, json, markdown
        # Load candidates
        if os.path.exists(candidate_file):
            with open(candidate_file, 'r') as f:
                try:
                    candidates = json.load(f)
                except Exception:
                    candidates = []
        else:
            candidates = []
        candidate = next((c for c in candidates if c.get('id') == candidate_id), None)
        if not candidate:
            return
        if 'probation_assessment_insights' not in candidate or not isinstance(candidate['probation_assessment_insights'], dict):
            candidate['probation_assessment_insights'] = {}
        # Hash for change detection
        pa_month_hash = hashlib.md5(json.dumps(assessment, sort_keys=True).encode()).hexdigest()
        insight_key = f'_pa_hash_{month}'
        # Only update if hash is missing or changed
        if (
            not candidate.get(insight_key)
            or candidate.get(insight_key) != pa_month_hash
            or not candidate['probation_assessment_insights'].get(str(month))
        ):
            user_input = f"Summarize the following probation assessment data for month {month}. Only use the information provided. Do not invent or assume anything. Be concise and factual.\nAssessment Data: {json.dumps(assessment, ensure_ascii=False)}"
            from Aion import chat_with_bot, SYSTEM_PROMPT
            insight = chat_with_bot(user_input, system_prompt=SYSTEM_PROMPT)
            try:
                insight_html = markdown.markdown(insight)
            except Exception:
                insight_html = insight
            candidate['probation_assessment_insights'][str(month)] = insight_html
            candidate[insight_key] = pa_month_hash
            # Save
            for idx, c in enumerate(candidates):
                if c.get('id') == candidate_id:
                    candidates[idx] = candidate
                    break
            with open(candidate_file, 'w') as f:
                json.dump(candidates, f, indent=4)
    threading.Thread(target=bg_generate_probation_insight, args=(candidate_id, month, assessment, candidate_file)).start()
    return redirect(url_for('candidate_profile', candidate_id=candidate_id, role=request.cookies.get('role', '')))


# Route to show candidate profile page
@app.route('/candidate/<int:candidate_id>')
def candidate_profile(candidate_id):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    candidate_file = os.path.join(db_folder, 'candidates.json')
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidates = json.load(f)
            except Exception:
                candidates = []
    else:
        candidates = []
    candidate = next((c for c in candidates if c.get('id') == candidate_id), None)
    if not candidate:
        return "Candidate not found", 404
    role = request.cookies.get('role', '')
    # Load probation assessment insights if present
    probation_insights = candidate.get('probation_assessment_insights', {}) if candidate else {}
    probation_assessment = candidate.get('probation_assessment', {}) if candidate else {}
    # Always pass schedule_interview to template for consistent logic
    schedule_interview = request.args.get('schedule_interview', False)
    if isinstance(schedule_interview, str):
        schedule_interview = schedule_interview.lower() == 'true'
    # Determine if Operation Manager should see the offer letter option
    show_offer_letter = False
    if candidate and candidate.get('status') == 'Pending Offer' and role == 'Operation Manager':
        show_offer_letter = True
    return render_template(
        'candidate_profile.html',
        candidate=candidate,
        role=role,
        probation_insights=probation_insights,
        probation_assessment=probation_assessment,
        schedule_interview=schedule_interview,
        show_offer_letter=show_offer_letter
    )




@app.route('/job/<job_id>')
def job_details(job_id):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    job_file = os.path.join(db_folder, 'jobs.json')
    jobs = []
    if os.path.exists(job_file):
        with open(job_file, 'r') as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    job = None
    for j in jobs:
        if str(j.get('job_id')) == str(job_id):
            job = j
            break
    if not job:
        return render_template('error.html', message='Job not found', role=request.cookies.get('role', ''))
    # Load uploaded CVs for this job and join with candidate details
    cv_file = os.path.join(db_folder, f'job_{job_id}_cvs.json')
    uploaded_cvs = []
    if os.path.exists(cv_file):
        with open(cv_file, 'r') as f:
            try:
                uploaded_cvs = json.load(f)
            except json.JSONDecodeError:
                uploaded_cvs = []
    # Load all candidates to join details
    candidate_file = os.path.join(db_folder, 'candidates.json')
    candidates = []
    if os.path.exists(candidate_file):
        with open(candidate_file, 'r') as f:
            try:
                candidates = json.load(f)
            except json.JSONDecodeError:
                candidates = []
    # Join candidate details to uploaded_cvs
    for cv in uploaded_cvs:
        # Ensure candidate_id is int for comparison
        cv_cand_id = cv.get('candidate_id')
        try:
            cv_cand_id_int = int(cv_cand_id)
        except (ValueError, TypeError):
            cv_cand_id_int = None
        candidate = next((c for c in candidates if c.get('id') == cv_cand_id_int), None)
        if candidate:
            cv['candidate_details'] = candidate
    return render_template('job_details.html', job=job, uploaded_cvs=uploaded_cvs, role=request.cookies.get('role', ''))

# Route to update job status
@app.route('/update_job_status/<job_id>', methods=['POST'])
def update_job_status(job_id):
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    job_file = os.path.join(db_folder, 'jobs.json')
    jobs = []
    if os.path.exists(job_file):
        with open(job_file, 'r') as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    job = None
    for j in jobs:
        if str(j.get('job_id')) == str(job_id):
            job = j
            break
    if job:
        status = request.form.get('status')
        job['status'] = status
        with open(job_file, 'w') as f:
            json.dump(jobs, f, indent=4)
        # Optionally, reload uploaded CVs for this job
        cv_file = os.path.join(db_folder, f'job_{job_id}_cvs.json')
        uploaded_cvs = []
        if os.path.exists(cv_file):
            with open(cv_file, 'r') as f:
                try:
                    uploaded_cvs = json.load(f)
                except json.JSONDecodeError:
                    uploaded_cvs = []
        return render_template('job_details.html', job=job, uploaded_cvs=uploaded_cvs, role=request.cookies.get('role', ''))
    else:
        return render_template('error.html', message='Job not found', role=request.cookies.get('role', ''))




# --- User Profile Route ---
@app.route('/profile')
def profile():
    logged_in_cookie = request.cookies.get('logged_in')
    is_logged_in = logged_in_cookie == 'true'
    username = request.cookies.get('username', '') if is_logged_in else ''
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    user_file = os.path.join(db_folder, 'userdata.json')
    user = None
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            try:
                users = json.load(f)
            except Exception:
                users = []
        user = next((u for u in users if u['username'] == username), None)
    if not user:
        # fallback: show empty profile or redirect to login
        return redirect(url_for('login'))
    # Add avatar_url fallback if missing
    if 'avatar_url' not in user or not user['avatar_url']:
        user['avatar_url'] = None
    return render_template('user_profile.html', user=user, role=user.get('role', ''))

# Dummy edit profile route for template link
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    return 'Edit Profile Page (to be implemented)'

@app.route('/manage_onboarding')
def manage_onboarding():
    candidates_list = fetch_candidate_data()  # from data.py
    role = request.cookies.get('role', '')
    view = request.args.get('view', 'table')
    return render_template('manage_onboarding.html', candidates_list=candidates_list, role=role, view=view)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)