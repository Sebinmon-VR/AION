# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_candidates_without_name(db_folder: str = "./db") -> str:
    """Deletes all candidates from candidates.json who do not have a name (empty or missing)."""
    import os, json
    file_path = os.path.join(db_folder, "candidates.json")
    if not os.path.exists(file_path):
        return f"⚠️ File {file_path} does not exist."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        original_count = len(candidates)
        filtered = [c for c in candidates if c.get("name", "").strip()]
        removed_count = original_count - len(filtered)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        if removed_count == 0:
            return "No candidates without a name were found."
        return f"✅ Deleted {removed_count} candidate(s) without a name."
    except Exception as e:
        return f"⚠️ Error deleting candidates: {e}"
import os
import json
import pytz
import subprocess
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_or_update_job_opening(
    job_title: str,
    job_posted_by: str,
    department: str = "",
    job_openings: int = 1,
    status: str = "open",
    job_location: str = "",
    job_type: str = "Full-time",
    job_requirements: str = "",
    job_description: str = "",
    job_lead_time: str = "",
    seniority_level: str = "",
    salary_range: str = "",
    jd_file_path: str = ""
) -> str:
    """Adds or updates a job opening in jobs.json."""
    import os, json, datetime
    file_path = os.path.join(os.path.dirname(__file__), "db", "jobs.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    else:
        jobs = []
    # Check if job already exists
    for job in jobs:
        if job.get("job_title", "").lower() == job_title.lower() and job.get("department", "").lower() == department.lower():
            job["job_openings"] = str(job_openings)
            job["status"] = status
            job["job_location"] = job_location
            job["job_type"] = job_type
            job["job_requirements"] = job_requirements
            job["job_description"] = job_description
            job["job_posted_by"] = job_posted_by
            job["job_lead_time"] = job_lead_time
            job["seniority_level"] = seniority_level
            job["salary_range"] = salary_range
            job["jd_file_path"] = jd_file_path
            job["posted_at"] = job.get("posted_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=4)
            return f"✅ Updated job opening for {job_title} in {department} to {job_openings} positions."
    # If not found, add new
    job_id = str(len(jobs) + 1)
    new_job = {
        "job_id": job_id,
        "job_title": job_title,
        "job_description": job_description,
        "job_location": job_location,
        "job_type": job_type,
        "job_requirements": job_requirements,
        "job_openings": str(job_openings),
        "job_posted_by": job_posted_by,
        "job_lead_time": job_lead_time,
        "department": department,
        "seniority_level": seniority_level,
        "salary_range": salary_range,
        "jd_file_path": jd_file_path,
        "posted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    }
    jobs.append(new_job)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4)
    return f"✅ Added new job opening for {job_title} in {department} with {job_openings} positions."

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_time(city: str) -> str:
    """Returns current time in the given city."""
    try:
        tz = pytz.timezone(city.replace(" ", "_"))
        return datetime.now(tz).strftime("%I:%M %p")
    except Exception:
        return f"Unknown city: {city}"
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def greet(name: str) -> str:
    """Greets a user by name."""
    return f"namaskaram, {name}!"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def update_json_file(file_path: str, data: Dict[str, Any]) -> str:
    """Updates a JSON file with the provided data."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                existing_data = json.load(file)
        else:
            existing_data = {}
        existing_data.update(data)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
        return f"✅ Successfully updated {file_path}"
    except Exception as e:
        return f"⚠️ Error updating JSON file: {e}"
        
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def read_db_files(db_folder: str = "./db") -> Dict[str, Any]:
    """Reads all JSON files in the specified database folder."""
    db_data = {}
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(db_folder):
            os.makedirs(db_folder, exist_ok=True)
            return db_data
            
        for filename in os.listdir(db_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(db_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    db_data[filename] = json.load(file)
    except Exception as e:
        print(f"Error reading database files: {e}")
    return db_data

def list_db_files(db_folder: str) -> Dict[str, str]:
    """Lists all JSON files in the specified database folder."""
    db_files = {}
    try:
        if not os.path.exists(db_folder):
            os.makedirs(db_folder, exist_ok=True)
            return db_files
            
        for filename in os.listdir(db_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(db_folder, filename)
                db_files[filename] = file_path
    except Exception as e:
        print(f"Error listing database files: {e}")
    return db_files

def create_json_file(filename: str, data: Dict[str, Any] = None, db_folder: str = "./db") -> str:
    """Creates a new JSON file with the provided data."""
    try:
        # Ensure the directory exists
        os.makedirs(db_folder, exist_ok=True)
        
        # Create the full file path
        file_path = os.path.join(db_folder, filename)
        
        # If no data provided, create empty dict
        if data is None:
            data = {}
        
        # Write the JSON file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        return f"✅ Successfully created {file_path}"
    except Exception as e:
        return f"⚠️ Error creating JSON file: {e}"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def clear_chat_history() -> str:
    """Clears all chat history and memory."""
    try:
        import sys
        import os
        # Get the parent directory to import Aion
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        from Aion import chat_history
        chat_history.clear_history()
        return "✅ Chat history cleared successfully."
    except Exception as e:
        return f"⚠️ Error clearing chat history: {e}"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_chat_summary() -> str:
    """Returns a summary of the current chat session."""
    try:
        import sys
        import os
        # Get the parent directory to import Aion
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        from Aion import chat_history
        total_messages = len(chat_history.messages)
        if total_messages == 0:
            return "No chat history available."
        
        user_messages = sum(1 for msg in chat_history.messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in chat_history.messages if msg["role"] == "assistant")
        tool_messages = sum(1 for msg in chat_history.messages if msg["role"] == "tool")
        
        return f"📊 Chat Summary:\n- Total messages: {total_messages}\n- User messages: {user_messages}\n- Assistant messages: {assistant_messages}\n- Tool executions: {tool_messages}"
    except Exception as e:
        return f"⚠️ Error getting chat summary: {e}"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def save_chat_export(filename: str = "chat_export.json") -> str:
    """Exports chat history to a specified file."""
    try:
        import sys
        import os
        # Get the parent directory to import Aion
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        from Aion import chat_history
        
        export_path = os.path.join("./db", filename)
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(chat_history.messages, f, ensure_ascii=False, indent=2)
        
        return f"✅ Chat history exported to {export_path}"
    except Exception as e:
        return f"⚠️ Error exporting chat history: {e}"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_json_file(filename: str, db_folder: str = "./db") -> str:
    """Deletes a JSON file from the specified database folder."""
    try:
        file_path = os.path.join(db_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"✅ Successfully deleted {file_path}"
        else:
            return f"⚠️ File {file_path} does not exist"
    except Exception as e:
        return f"⚠️ Error deleting file: {e}"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def read_json_file(filename: str, db_folder: str = "./db") -> Dict[str, Any]:
    """Reads a specific JSON file from the database folder."""
    try:
        file_path = os.path.join(db_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return {"error": f"File {filename} does not exist"}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def check_db_status(db_folder: str = "./db") -> str:
    """Checks the status of the database folder and its contents."""
    try:
        if not os.path.exists(db_folder):
            return f"📁 Database folder '{db_folder}' does not exist."
        
        files = [f for f in os.listdir(db_folder) if f.endswith('.json')]
        total_files = len(files)
        
        if total_files == 0:
            return f"📁 Database folder '{db_folder}' exists but is empty."
        
        status = f"📁 Database folder '{db_folder}' contains {total_files} JSON files:\n"
        for file in files:
            file_path = os.path.join(db_folder, file)
            size = os.path.getsize(file_path)
            status += f"  - {file} ({size} bytes)\n"
        
        return status.strip()
    except Exception as e:
        return f"⚠️ Error checking database status: {e}"

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_charts(data: Any, chart_type: str = "bar") -> str:
    """Creates charts based on the provided data.
    
    Data can be:
    - List of dicts: [{'category': 'A', 'value': 10}, ...]
    - Dict: {'A': 10, 'B': 20, ...}
    - JSON string of either format above
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        
        # Handle different data formats
        if isinstance(data, str):
            # If it's a JSON string, parse it
            import json
            data = json.loads(data)
        
        if isinstance(data, dict):
            # Convert dict to list of dicts format
            data = [{'category': k, 'value': v} for k, v in data.items()]
        elif isinstance(data, list):
            # Check if it's already in the correct format
            if data and isinstance(data[0], dict):
                # Ensure it has the right keys
                if 'category' not in data[0] or 'value' not in data[0]:
                    # Try to infer the structure
                    if len(data[0]) == 2:
                        keys = list(data[0].keys())
                        data = [{'category': item[keys[0]], 'value': item[keys[1]]} for item in data]
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        if chart_type == "bar":
            plt.figure(figsize=(10, 6))
            sns.barplot(data=df, x='category', y='value')
            plt.title("Bar Chart")
            plt.xlabel("Categories")
            plt.ylabel("Values")
            chart_path = "./db/bar_chart.png"
            plt.savefig(chart_path)
            plt.close()
            return f"✅ Bar chart created at {chart_path}"
        elif chart_type == "line":
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=df, x='category', y='value')
            plt.title("Line Chart")
            plt.xlabel("Categories")
            plt.ylabel("Values")
            chart_path = "./db/line_chart.png"
            plt.savefig(chart_path)
            plt.close()
            return f"✅ Line chart created at {chart_path}"
        else:
            return "⚠️ Unsupported chart type. Please use 'bar' or 'line'."
    except ImportError:
        return "⚠️ Required libraries for chart creation are not installed. Please install matplotlib and seaborn."
    except Exception as e:
        return f"⚠️ Error creating chart: {e}. Expected format: {{'category1': value1, 'category2': value2}} or [{'category': 'name', 'value': number}]"
    
def create_pie_chart(data: Any) -> str:
    """Creates a pie chart based on the provided data.
    
    Data can be:
    - List of dicts with 'category' and 'value' keys: [{'category': 'A', 'value': 10}, ...]
    - Dict with category names as keys and values: {'A': 10, 'B': 20, ...}
    - JSON string of either format above
    """
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        
        # Handle different data formats
        if isinstance(data, str):
            # If it's a JSON string, parse it
            import json
            data = json.loads(data)
        
        if isinstance(data, dict):
            # Convert dict to list of dicts format
            data = [{'category': k, 'value': v} for k, v in data.items()]
        elif isinstance(data, list):
            # Check if it's already in the correct format
            if data and isinstance(data[0], dict):
                # Ensure it has the right keys
                if 'category' not in data[0] or 'value' not in data[0]:
                    # Try to infer the structure
                    if len(data[0]) == 2:
                        keys = list(data[0].keys())
                        data = [{'category': item[keys[0]], 'value': item[keys[1]]} for item in data]
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(df['value'], labels=df['category'], autopct='%1.1f%%', startangle=140)
        plt.title("Pie Chart")
        chart_path = "./db/pie_chart.png"
        plt.savefig(chart_path)
        plt.close()
        return f"✅ Pie chart created at {chart_path}"
        
    except ImportError:
        return "⚠️ Required libraries for pie chart creation are not installed. Please install matplotlib and pandas."
    except Exception as e:
        return f"⚠️ Error creating pie chart: {e}. Expected format: {{'category1': value1, 'category2': value2}} or [{'category': 'name', 'value': number}]"
    


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

