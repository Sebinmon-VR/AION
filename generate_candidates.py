import json
import random
from datetime import datetime, timedelta
import uuid

# Load existing candidates
with open('db/candidates.json', 'r') as f:
    existing_candidates = json.load(f)

# Get the next available ID
next_id = max([c.get('id', 0) for c in existing_candidates]) + 1

# Job positions from the jobs.json
jobs_data = [
    {'job_id': '1', 'position': 'SP3D Designer', 'department': 'Digitization', 'seniority': 'Mid'},
    {'job_id': '2', 'position': 'SP3D Admin.', 'department': 'Digitization', 'seniority': 'Mid'},
    {'job_id': '3', 'position': 'SP3D Designer', 'department': 'Digital', 'seniority': 'Senior'},
    {'job_id': '4', 'position': 'SP3D Admin', 'department': 'Piping', 'seniority': 'Mid'},
    {'job_id': '5', 'position': 'Sr. SP3D Designer', 'department': 'Civil/Structural', 'seniority': 'Senior'},
    {'job_id': '6', 'position': 'Sr. SP3D Admin.', 'department': 'E&I', 'seniority': 'Senior'},
    {'job_id': '7', 'position': 'SPI Designer', 'department': 'I&C', 'seniority': 'Mid'},
    {'job_id': '8', 'position': 'SPI Admin', 'department': 'I&C', 'seniority': 'Mid'},
    {'job_id': '9', 'position': 'SPI Designer', 'department': 'I&C', 'seniority': 'Mid'},
    {'job_id': '10', 'position': 'SPI Admin', 'department': 'I&C', 'seniority': 'Mid'},
    {'job_id': '11', 'position': 'Sr. SPI Designer', 'department': 'I&C', 'seniority': 'Senior'},
    {'job_id': '12', 'position': 'Sr. SPI Admin', 'department': 'I&C', 'seniority': 'Lead'},
    {'job_id': '13', 'position': 'SPEL Designer', 'department': 'Electrical', 'seniority': 'Junior'},
    {'job_id': '14', 'position': 'SPEL Admin', 'department': 'Electrical', 'seniority': 'Junior'},
    {'job_id': '15', 'position': 'SPEL Designer', 'department': 'Electrical', 'seniority': 'Mid'},
    {'job_id': '16', 'position': 'SPEL Admin', 'department': 'Electrical', 'seniority': 'Mid'},
    {'job_id': '17', 'position': 'Sr. SPEL Designer', 'department': 'Electrical', 'seniority': 'Manager'}
]

# Sample names, emails, and phone numbers
first_names = [
    "Ahmed", "Fatima", "Mohammed", "Aisha", "Omar", "Nour", "Ali", "Maryam", "Hassan", "Layla",
    "Khaled", "Zara", "Ibrahim", "Salma", "Youssef", "Amina", "Tariq", "Yasmin", "Saeed", "Lina",
    "Abdul", "Huda", "Majid", "Rania", "Waleed", "Dina", "Mansour", "Reem", "Karim", "Hala",
    "John", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Ashley", "James", "Lisa",
    "William", "Anna", "Richard", "Emma", "Joseph", "Olivia", "Thomas", "Sophia", "Christopher", "Isabella",
    "Rajesh", "Priya", "Amit", "Sunita", "Vikash", "Meera", "Arjun", "Kavya", "Rohan", "Anita",
    "Kiran", "Neha", "Anil", "Pooja", "Rahul", "Shreya", "Sanjay", "Divya", "Manoj", "Rekha",
    "Chen", "Li", "Wang", "Zhang", "Liu", "Yang", "Huang", "Zhao", "Wu", "Zhou",
    "Hiroshi", "Yuki", "Takeshi", "Akiko", "Kenji", "Emi", "Satoshi", "Naoko", "Masaki", "Yoko",
    "Pierre", "Marie", "Jean", "Sophie", "Antoine", "Claire", "Laurent", "Camille", "Nicolas", "Isabelle"
]

last_names = [
    "Al-Rashid", "Al-Mansouri", "Al-Zahra", "Al-Ahmad", "Al-Hassan", "Al-Mahmoud", "Al-Najjar", "Al-Khoury",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Yadav", "Mishra", "Agarwal", "Jain", "Verma",
    "Li", "Wang", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou",
    "Tanaka", "Suzuki", "Takahashi", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato", "Yoshida",
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau"
]

# Technical skills based on job types
sp3d_skills = ["SP3D", "AutoCAD", "SmartPlant", "Piping Design", "3D Modeling", "PDMS", "PDS", "Plant Design"]
spi_skills = ["SPI", "SmartPlant Instrumentation", "P&ID", "Instrument Design", "Control Systems", "DCS", "PLC", "SCADA"]
spel_skills = ["SPEL", "Electrical Design", "AutoCAD Electrical", "Power Systems", "Motor Control", "Lighting Design", "Earthing Systems"]
admin_skills = ["Database Management", "System Administration", "User Training", "Project Coordination", "Quality Control", "Documentation"]

# Companies for experience
companies = [
    "ADNOC", "Saudi Aramco", "Qatar Petroleum", "SABIC", "Emirates Steel", "Borouge", "TAKREER",
    "Jacobs", "Worley", "Wood", "Technip", "Saipem", "McDermott", "Fluor", "KBR", "Bechtel",
    "Petrofac", "Amec Foster Wheeler", "NPCC", "Dodsal", "Larsen & Toubro", "Punj Lloyd", "Essar",
    "Tata Projects", "Samsung Engineering", "Hyundai Engineering", "Daewoo", "JGC Corporation",
    "Chiyoda Corporation", "Toyo Engineering", "Mitsubishi Heavy Industries", "Yokogawa",
    "ABB", "Siemens", "Schneider Electric", "Honeywell", "Emerson", "Rockwell Automation"
]

# Interview transcripts for different positions
interview_transcripts = {
    "SP3D": "Thank you for joining us today. Let me start by asking about your experience with SP3D software. I've been working with SP3D for about 6 years now, starting as a junior designer and gradually taking on more complex projects. In my current role, I'm responsible for creating detailed 3D piping models, generating isometric drawings, and ensuring clash detection is properly executed. I've worked on several major projects including a gas processing plant and an oil refinery expansion. One of my key achievements was optimizing the piping layout which resulted in 15% material savings for the client. I'm also proficient in integrating SP3D with other software like PDMS and AutoCAD for comprehensive plant design workflows.",
    
    "SPI": "Can you walk me through your experience with SmartPlant Instrumentation? Certainly. I have 5 years of hands-on experience with SPI, focusing primarily on instrumentation and control systems design. I've been involved in creating P&ID drawings, instrument specifications, and hook-up drawings for various industrial projects. My expertise includes loop checking, instrument sizing, and integration with control systems like DCS and PLC. I've worked on petrochemical plants where accuracy and compliance with international standards like ISA and IEC were critical. I'm particularly proud of a project where I led the instrumentation design for a new distillation unit, coordinating with process engineers to ensure optimal control strategy implementation.",
    
    "SPEL": "Tell me about your electrical design experience using SPEL. I have extensive experience with SPEL software spanning 7 years in electrical design for industrial facilities. My work primarily involves designing electrical distribution systems, motor control centers, and lighting layouts for oil and gas facilities. I'm well-versed in international electrical standards including IEC, IEEE, and local UAE regulations. I've successfully designed electrical systems for offshore platforms, onshore processing facilities, and power distribution networks. My recent project involved the complete electrical design for a 150MW power generation facility where I was responsible for the main electrical equipment selection, protection coordination, and grounding system design."
}

# AI interview analysis templates
ai_analysis_templates = [
    "**Comprehensive Performance Summary:**\nThe candidate demonstrated strong technical competency and clear communication throughout the interview. They showed practical understanding of {software} software and its applications in {domain} projects. Their responses indicated hands-on experience with real-world challenges and solutions.\n\n**Specific Feedback:**\n- **Technical Knowledge:** Excellent grasp of {software} functionalities and industry best practices. Score: {tech_score}/10\n- **Communication Skills:** Clear and professional communication with good use of technical terminology. Score: {comm_score}/10\n- **Problem-Solving:** Demonstrated analytical thinking and practical approach to technical challenges. Score: {prob_score}/10\n- **Experience Relevance:** Strong alignment with job requirements and relevant project experience. Score: {exp_score}/10\n\n**Areas for Improvement:**\n- Could benefit from exposure to latest software updates and industry trends\n- Recommend continuous learning in emerging technologies\n\n**Final Performance Score:** {total_score}/100",
    
    "**Interview Assessment Summary:**\nCandidate showed solid foundation in {software} with {years} years of experience. They demonstrated competency in technical aspects and showed enthusiasm for the role. Communication was effective and professional throughout the session.\n\n**Technical Evaluation:**\n- **Software Proficiency:** {software} - Advanced level with practical project experience\n- **Industry Knowledge:** Good understanding of {domain} sector requirements\n- **Project Management:** Experience in coordinating with multi-disciplinary teams\n- **Quality Standards:** Awareness of international standards and best practices\n\n**Behavioral Assessment:**\n- **Teamwork:** Collaborative approach with good interpersonal skills\n- **Adaptability:** Flexible and open to learning new technologies\n- **Leadership:** Shows potential for taking on senior responsibilities\n\n**Recommendation:** {recommendation}\n**Overall Score:** {total_score}/100"
]

# Status options with weights (more likely to be in earlier stages)
status_options = [
    ("New", 20),
    ("Shortlisted", 25),
    ("Interview Scheduled", 15),
    ("Interviewed", 20),
    ("Selected", 8),
    ("Hired", 10),
    ("Rejected", 2)
]

# Weighted random selection function
def weighted_choice(choices):
    total = sum(weight for choice, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        if upto + weight >= r:
            return choice
        upto += weight
    return choices[-1][0]

# Generate candidates
new_candidates = []
managers = ["mike", "kevin", "jhon", "sara", "discipline_mgr_elec", "discipline_mgr_inst", "discipline_mgr_digi"]

for i in range(100):
    candidate_id = next_id + i
    
    # Select random job
    job = random.choice(jobs_data)
    
    # Generate candidate basic info
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"
    
    # Generate email
    email_variations = [
        f"{first_name.lower()}.{last_name.lower()}@gmail.com",
        f"{first_name.lower()}{last_name.lower()}@outlook.com",
        f"{first_name.lower()}{random.randint(10,99)}@yahoo.com",
        f"{last_name.lower()}{first_name.lower()}@hotmail.com"
    ]
    email = random.choice(email_variations)
    
    # Generate phone number
    phone_formats = [
        f"+971-50-{random.randint(1000000,9999999)}",
        f"+971-55-{random.randint(1000000,9999999)}",
        f"(0{random.randint(10,99)}){random.randint(100,999)}-{random.randint(1000,9999)}",
        f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(1000,9999)}"
    ]
    phone = random.choice(phone_formats)
    
    # Select skills based on position
    if "SP3D" in job['position']:
        base_skills = random.sample(sp3d_skills, random.randint(4, 6))
        interview_type = "SP3D"
        domain = "piping and plant design"
    elif "SPI" in job['position']:
        base_skills = random.sample(spi_skills, random.randint(4, 6))
        interview_type = "SPI"
        domain = "instrumentation and control"
    elif "SPEL" in job['position']:
        base_skills = random.sample(spel_skills, random.randint(4, 6))
        interview_type = "SPEL"
        domain = "electrical systems"
    else:
        base_skills = random.sample(sp3d_skills + admin_skills, random.randint(4, 6))
        interview_type = "SP3D"
        domain = "plant design"
    
    if "Admin" in job['position']:
        base_skills.extend(random.sample(admin_skills, random.randint(2, 3)))
    
    # Generate experience
    experience_years = random.randint(2, 15)
    experience_list = []
    for exp_i in range(random.randint(2, 4)):
        company = random.choice(companies)
        role_types = ["Designer", "Engineer", "Specialist", "Coordinator", "Analyst", "Supervisor"]
        role = random.choice(role_types)
        years = random.randint(1, 5)
        experience_list.append(f"{company} – {role} – {years} years")
    
    # Generate education
    education_options = [
        "Bachelor of Engineering in Mechanical Engineering",
        "Bachelor of Engineering in Electrical Engineering", 
        "Bachelor of Engineering in Chemical Engineering",
        "Bachelor of Engineering in Civil Engineering",
        "Bachelor of Technology in Instrumentation",
        "Master of Engineering in Process Engineering",
        "Diploma in Plant Design Engineering"
    ]
    education = [random.choice(education_options)] if random.choice([True, False]) else []
    
    # Generate certifications
    cert_options = [
        "SP3D Certified Professional",
        "AutoCAD Professional Certification",
        "Project Management Professional (PMP)",
        "Certified Instrumentation Engineer",
        "Electrical Safety Certification",
        "ISO 9001 Quality Management"
    ]
    certifications = random.sample(cert_options, random.randint(0, 3))
    
    # Generate match score
    match_score = random.randint(5, 9)
    
    # Generate dates
    base_date = datetime.now() - timedelta(days=random.randint(1, 180))
    applied_date = base_date.strftime("%Y-%m-%d")
    
    # Select status
    status = weighted_choice(status_options)
    
    # Generate status history and related fields
    status_history = []
    current_date = base_date
    
    # Initial CV upload
    status_history.append({
        "from_status": "None",
        "to_status": "New", 
        "updated_by": "System (CV Upload)",
        "updated_by_role": "Automated",
        "updated_at": current_date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "update_type": "cv_upload"
    })
    
    manager = random.choice(managers)
    milestone_dates = {}
    
    # Progress through statuses
    status_progression = ["New", "Shortlisted", "Interview Scheduled", "Interviewed", "Selected", "Hired"]
    final_status_index = status_progression.index(status) if status in status_progression else 0
    
    for status_idx in range(1, final_status_index + 1):
        current_date += timedelta(days=random.randint(1, 7))
        from_status = status_progression[status_idx - 1]
        to_status = status_progression[status_idx]
        
        if to_status == "Shortlisted":
            milestone_dates["shortlisted_date"] = current_date.strftime("%Y-%m-%d")
            
        elif to_status == "Interview Scheduled":
            milestone_dates["interview_scheduled_date"] = current_date.strftime("%Y-%m-%d")
            milestone_dates["interview_date"] = current_date.strftime("%Y-%m-%d")
            milestone_dates["interview_time"] = f"{random.randint(9,17)}:{random.randint(10,59):02d}"
            milestone_dates["intervier"] = manager
            
        elif to_status == "Interviewed":
            milestone_dates["interviewed_date"] = current_date.strftime("%Y-%m-%d")
            
        elif to_status == "Selected":
            milestone_dates["selected_date"] = current_date.strftime("%Y-%m-%d")
            
        elif to_status == "Hired":
            milestone_dates["hired_date"] = current_date.strftime("%Y-%m-%d")
        
        status_history.append({
            "from_status": from_status,
            "to_status": to_status,
            "updated_by": manager,
            "updated_by_role": "Discipline Manager",
            "updated_at": current_date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "update_type": "interview_scheduled" if to_status == "Interview Scheduled" else "manual_status_update",
            **({"interview_date": milestone_dates.get("interview_date"), 
                "interview_time": milestone_dates.get("interview_time"),
                "interviewer": manager} if to_status == "Interview Scheduled" else {})
        })
    
    # Create candidate object
    candidate = {
        "id": candidate_id,
        "name": name,
        "email": email,
        "phone": phone,
        "position": job['position'],
        "status": status,
        "resume_link": "",
        "cv_path": f"resumes/cv_{random.randint(1000000,9999999)}.{'pdf' if random.choice([True, False]) else 'docx'}",
        "applied_date": applied_date,
        "notes": "",
        "skills": base_skills,
        "experience": experience_list,
        "education": education,
        "certifications": certifications,
        "projects": [],
        "linkedin": None,
        "github": None,
        "match_score": match_score,
        "job_id": job['job_id'],
        "status_updated_by": manager if status != "New" else "System (CV Upload)",
        "status_updated_by_role": "Discipline Manager" if status != "New" else "Automated",
        "status_updated_at": current_date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "previous_status": status_progression[final_status_index - 1] if final_status_index > 0 else "None",
        "status_history": status_history
    }
    
    # Add milestone dates
    candidate.update(milestone_dates)
    
    # Add interview data if interviewed
    if status in ["Interviewed", "Selected", "Hired"]:
        software = interview_type
        template = random.choice(ai_analysis_templates)
        
        tech_score = random.randint(7, 10)
        comm_score = random.randint(6, 9) 
        prob_score = random.randint(6, 9)
        exp_score = random.randint(7, 10)
        total_score = random.randint(70, 95)
        
        recommendation = "Recommended for hiring" if total_score >= 80 else "Consider for next round"
        
        candidate.update({
            "interview_transcript": interview_transcripts[interview_type],
            "ai_interview_report": template.format(
                software=software,
                domain=domain,
                years=experience_years,
                tech_score=tech_score,
                comm_score=comm_score,
                prob_score=prob_score,
                exp_score=exp_score,
                total_score=total_score,
                recommendation=recommendation
            ),
            "interview_score": total_score,
            "interview_analyzed_at": current_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        })
    
    new_candidates.append(candidate)

# Combine with existing candidates
all_candidates = existing_candidates + new_candidates

# Save updated candidates file
with open('db/candidates.json', 'w') as f:
    json.dump(all_candidates, f, indent=4)

print(f"Generated {len(new_candidates)} new candidates")
print(f"Total candidates: {len(all_candidates)}")

# Print summary by job
job_summary = {}
for candidate in all_candidates:
    job_id = candidate['job_id']
    if job_id not in job_summary:
        job_summary[job_id] = {'total': 0, 'hired': 0, 'interviewed': 0}
    job_summary[job_id]['total'] += 1
    if candidate['status'] == 'Hired':
        job_summary[job_id]['hired'] += 1
    if candidate['status'] in ['Interviewed', 'Selected', 'Hired']:
        job_summary[job_id]['interviewed'] += 1

print("\nCandidate Summary by Job:")
for job_id, stats in sorted(job_summary.items()):
    print(f"Job {job_id}: {stats['total']} total, {stats['interviewed']} interviewed, {stats['hired']} hired")
