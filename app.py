from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import datetime
import sys
from data import *
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

load_dotenv(override=True)
app = Flask(__name__)
CORS(app)   
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

@app.route('/')
def index():
    logged_in_cookie = request.cookies.get('logged_in')
    is_logged_in = logged_in_cookie == 'true'
    if is_logged_in:
        role = request.cookies.get('role', '')
        username = request.cookies.get('username', '')
        email = request.cookies.get('email', '')
        phone = request.cookies.get('phone', '')
        department = request.cookies.get('department', '')
        time= datetime.datetime.now().strftime("%H:%M:%S")
        greeting = "Good Morning" if int(time.split(':')[0]) < 12 else "Good Afternoon" if int(time.split(':')[0]) < 18 else "Good Evening"
        access_control = []
        
        if username:
            db_folder = os.path.join(os.path.dirname(__file__), 'db')
            user_file = os.path.join(db_folder, 'userdata.json')
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    try:
                        users = json.load(f)
                    except json.JSONDecodeError:
                        users = []
                user = next((u for u in users if u['username'] == username), None)
                if user:
                    access_control = user.get('access_control', [])
        return render_template('dashboard.html',logged_in=True,
                               username=username,
                               email=email,
                               phone=phone,
                               department=department,
                               role=role,
                               access_control=access_control, 
                               is_logged_in=is_logged_in , 
                               greeting=greeting ,
                               job_count=job_count(),
                               openings=openings_count(),
                               users=fetch_user_data(),
                               user_count=total_users(), 
                               candidate_count=candidate_count(),
                               candidates_list=fetch_candidate_data(),
                               
                               )
    else:
        return render_template('login.html', logged_in=False, is_logged_in=is_logged_in)

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
        access_control_map = {
            'HR Executive': ["post_jobs", "manage_candidates", "manage_onboarding"],
            'HR Manager': ["post_jobs", "manage_candidates", "manage_onboarding", "manage_hr_team"],
            'Hiring Manager': ["view_candidates", "interview_candidates", "manage_onboarding", "manage_hr_team", "approve_hiring"],
            'HR Director': ["manage_hr_team", "approve_hiring", "manage_onboarding", "view_all_hr"],
            'HR Admin': ["manage_users", "manage_hr_team", "view_all_hr"],
            'CEO': ["view_all_hr", "approve_hiring", "manage_admins", "manage_hr_team"],
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
        return render_template('signup.html', error='All fields are required'), 400

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/jobs_list')
def jobs_list():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    job_file = os.path.join(db_folder, 'jobs.json')
    jobs = []
    if os.path.exists(job_file):
        with open(job_file, 'r') as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    return render_template('jobs_list.html', jobs=jobs ,role=request.cookies.get('role', ''))

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/post_jobs', methods=['POST', 'GET'])
def post_jobs():
    logged_in_cookie = request.cookies.get('logged_in')
    is_logged_in = logged_in_cookie == 'true'
    if not is_logged_in:
        # If not logged in, redirect to login page for both GET and POST
        return redirect(url_for('login'))
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        job_location = request.form.get('job_location')
        job_type = request.form.get('job_type')
        job_openings = request.form.get('job_openings')
        job_posted_by = request.cookies.get('username', 'Unknown')
        job_lead_time = request.form.get('lead_time', 'Immediate')
        job_requirements = request.form.get('job_requirements')
        job_data = {
            'job_title': job_title,
            'job_description': job_description,
            'job_location': job_location,
            'job_type': job_type,
            'job_requirements': job_requirements,
            'job_openings': job_openings,
            'job_posted_by': job_posted_by,
            'job_lead_time': job_lead_time,
            'posted_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        }
        db_folder = os.path.join(os.path.dirname(__file__), 'db')
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
        job_file = os.path.join(db_folder, 'jobs.json')
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                try:
                    jobs = json.load(f)
                except json.JSONDecodeError:
                    jobs = []
        else:
            jobs = []
        jobs.append(job_data)
        with open(job_file, 'w') as f:
            json.dump(jobs, f, indent=4)
        return redirect(url_for('jobs_list'))
    return render_template('post_jobs.html', is_logged_in=is_logged_in)

# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_candidates')
def manage_candidates():
    return render_template('manage_candidates.html' ,role=request.cookies.get('role', ''))
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_onboarding')
def manage_onboarding():
    return render_template('manage_onboarding.html',role=request.cookies.get('role', ''))
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/manage_hr_team')
def manage_hr_team():
    return render_template('manage_hr_team.html',role=request.cookies.get('role', ''))
# ---------------------------------------------------------------------------------------------------------------------

@app.route('/approve_hiring')
def approve_hiring():
    return render_template('approve_hiring.html',role=request.cookies.get('role', ''))
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
# ---------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)