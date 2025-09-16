import pandas as pd
import random
from datetime import datetime, timedelta
import json

def generate_synthetic_patients(num_patients=50):
    """Generate synthetic patient data for testing"""
    
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
        "William", "Ashley", "James", "Amanda", "Christopher", "Jennifer", "Daniel",
        "Lisa", "Matthew", "Nancy", "Anthony", "Karen", "Mark", "Betty", "Donald",
        "Helen", "Steven", "Sandra", "Paul", "Donna", "Andrew", "Carol", "Joshua",
        "Ruth", "Kenneth", "Sharon", "Kevin", "Michelle", "Brian", "Laura", "George",
        "Sarah", "Edward", "Kimberly", "Ronald", "Deborah", "Timothy", "Dorothy",
        "Jason", "Lisa", "Jeffrey", "Nancy", "Ryan", "Karen", "Jacob", "Betty"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
        "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell"
    ]
    
    insurance_carriers = [
        "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth", "Humana",
        "Kaiser Permanente", "Anthem", "Molina Healthcare", "Centene", "WellCare"
    ]
    
    doctors = [
        {"name": "Dr. Sarah Johnson", "specialty": "Internal Medicine", "location": "Main Campus"},
        {"name": "Dr. Michael Chen", "specialty": "Cardiology", "location": "Main Campus"},
        {"name": "Dr. Emily Rodriguez", "specialty": "Pediatrics", "location": "Pediatric Wing"},
        {"name": "Dr. David Kim", "specialty": "Orthopedics", "location": "Sports Medicine Center"},
        {"name": "Dr. Lisa Thompson", "specialty": "Dermatology", "location": "Main Campus"}
    ]
    
    patients = []
    
    for i in range(num_patients):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = datetime.now() - timedelta(days=random.randint(18*365, 80*365))
        
        patient = {
            "patient_id": f"PAT{i+1:03d}",
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "phone": f"{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
            "insurance_carrier": random.choice(insurance_carriers),
            "member_id": f"INS{random.randint(100000, 999999)}",
            "group_number": f"GRP{random.randint(1000, 9999)}",
            "is_new_patient": random.choice([True, False]),
            "preferred_doctor": random.choice(doctors)["name"],
            "last_visit": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d") if random.random() > 0.3 else None,
            "emergency_contact": f"{random.choice(first_names)} {random.choice(last_names)}",
            "emergency_phone": f"{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Cedar Ln'])}",
            "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
            "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
            "zip_code": f"{random.randint(10000, 99999)}"
        }
        patients.append(patient)
    
    return patients

def generate_doctor_schedules():
    """Generate doctor availability schedules"""
    
    doctors = [
        {"name": "Dr. Sarah Johnson", "specialty": "Internal Medicine", "location": "Main Campus"},
        {"name": "Dr. Michael Chen", "specialty": "Cardiology", "location": "Main Campus"},
        {"name": "Dr. Emily Rodriguez", "specialty": "Pediatrics", "location": "Pediatric Wing"},
        {"name": "Dr. David Kim", "specialty": "Orthopedics", "location": "Sports Medicine Center"},
        {"name": "Dr. Lisa Thompson", "specialty": "Dermatology", "location": "Main Campus"}
    ]
    
    schedules = []
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for doctor in doctors:
        for day in range(30):  # Next 30 days
            current_date = start_date + timedelta(days=day)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
                
            # Generate morning and afternoon slots
            morning_start = current_date.replace(hour=9, minute=0)
            morning_end = current_date.replace(hour=12, minute=0)
            
            afternoon_start = current_date.replace(hour=13, minute=0)
            afternoon_end = current_date.replace(hour=17, minute=0)
            
            # Morning slots (9 AM - 12 PM)
            current_time = morning_start
            while current_time < morning_end:
                schedules.append({
                    "doctor_name": doctor["name"],
                    "specialty": doctor["specialty"],
                    "location": doctor["location"],
                    "date": current_date.strftime("%Y-%m-%d"),
                    "start_time": current_time.strftime("%H:%M"),
                    "end_time": (current_time + timedelta(minutes=30)).strftime("%H:%M"),
                    "is_available": random.choice([True, True, True, False])  # 75% availability
                })
                current_time += timedelta(minutes=30)
            
            # Afternoon slots (1 PM - 5 PM)
            current_time = afternoon_start
            while current_time < afternoon_end:
                schedules.append({
                    "doctor_name": doctor["name"],
                    "specialty": doctor["specialty"],
                    "location": doctor["location"],
                    "date": current_date.strftime("%Y-%m-%d"),
                    "start_time": current_time.strftime("%H:%M"),
                    "end_time": (current_time + timedelta(minutes=30)).strftime("%H:%M"),
                    "is_available": random.choice([True, True, True, False])  # 75% availability
                })
                current_time += timedelta(minutes=30)
    
    return schedules

def create_sample_data():
    """Create and save sample data files"""
    
    # Generate patients
    patients = generate_synthetic_patients(50)
    patients_df = pd.DataFrame(patients)
    patients_df.to_csv("data/patients.csv", index=False)
    
    # Generate doctor schedules
    schedules = generate_doctor_schedules()
    schedules_df = pd.DataFrame(schedules)
    schedules_df.to_excel("data/doctor_schedules.xlsx", index=False)
    
    # Create sample intake forms
    intake_forms = {
        "new_patient_form": {
            "form_name": "New Patient Intake Form",
            "fields": [
                "Medical History",
                "Current Medications",
                "Allergies",
                "Emergency Contact",
                "Insurance Information",
                "Previous Medical Records"
            ],
            "template_path": "templates/new_patient_form.html"
        },
        "returning_patient_form": {
            "form_name": "Returning Patient Update Form",
            "fields": [
                "Updated Medical History",
                "Current Medications",
                "New Allergies",
                "Insurance Updates",
                "Reason for Visit"
            ],
            "template_path": "templates/returning_patient_form.html"
        }
    }
    
    with open("data/intake_forms.json", "w") as f:
        json.dump(intake_forms, f, indent=2)
    
    print("Sample data generated successfully!")
    print(f"Generated {len(patients)} patients")
    print(f"Generated {len(schedules)} appointment slots")
    
    return patients_df, schedules_df

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    create_sample_data()
