import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = "https://wwfraugezutgfefjvlwq.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Supabase connected successfully (AddDatatoDatabase)")

# 🧠 Student data dictionary
data = {
    "6003": {
        "name": "ARJUN KUMAR VERMA",
        "major": "Artificial Intelligence Engineer",
        "starting_year": 2023,
        "total_attendance": 7,
        "standing": "G",
        "year": 3,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "6004": {
        "name": "Nitesh Prajapati",
        "major": "Software Engineer",
        "starting_year": 2023,
        "total_attendance": 4,
        "standing": "B",
        "year": 1,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "6005": {
"name": "Varun Kumar Mishra",
        "major": "AI/ML Engineer",
        "starting_year": 2023,
        "total_attendance": 7,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34"
    }
}

# 📤 Upload data to Supabase
for student_id, info in data.items():
    record = {"student_id": student_id, **info}
    response = supabase.table("Students").insert(record).execute()
    print(f"📤 Inserted: {student_id} → {response}")

print("✅ All student data uploaded successfully to Supabase.")
