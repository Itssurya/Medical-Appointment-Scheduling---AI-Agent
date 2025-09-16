import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
import os

class MedicalDatabase:
    """Database management for medical appointment scheduling system"""
    
    def __init__(self, db_path: str = "medical_appointments.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                insurance_carrier TEXT,
                member_id TEXT,
                group_number TEXT,
                is_new_patient BOOLEAN DEFAULT 1,
                preferred_doctor TEXT,
                last_visit TEXT,
                emergency_contact TEXT,
                emergency_phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Appointments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                status TEXT DEFAULT 'scheduled',
                reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        ''')
        
        # Doctor schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT NOT NULL,
                reminder_type TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
            )
        ''')
        
        # Forms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forms (
                form_id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT NOT NULL,
                form_type TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_patients_from_csv(self, csv_path: str):
        """Load patients from CSV file"""
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO patients 
                (patient_id, first_name, last_name, date_of_birth, phone, email,
                 insurance_carrier, member_id, group_number, is_new_patient,
                 preferred_doctor, last_visit, emergency_contact, emergency_phone,
                 address, city, state, zip_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['patient_id'], row['first_name'], row['last_name'],
                row['date_of_birth'], row['phone'], row['email'],
                row['insurance_carrier'], row['member_id'], row['group_number'],
                row['is_new_patient'], row['preferred_doctor'], row['last_visit'],
                row['emergency_contact'], row['emergency_phone'], row['address'],
                row['city'], row['state'], row['zip_code']
            ))
        
        conn.commit()
        conn.close()
        print(f"Loaded {len(df)} patients from {csv_path}")
    
    def load_schedules_from_excel(self, excel_path: str):
        """Load doctor schedules from Excel file"""
        if not os.path.exists(excel_path):
            print(f"Excel file not found: {excel_path}")
            return
        
        df = pd.read_excel(excel_path)
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO doctor_schedules 
                (doctor_name, specialty, location, date, start_time, end_time, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['doctor_name'], row['specialty'], row['location'],
                row['date'], row['start_time'], row['end_time'], row['is_available']
            ))
        
        conn.commit()
        conn.close()
        print(f"Loaded {len(df)} schedule slots from {excel_path}")
    
    def find_patient(self, first_name: str, last_name: str, dob: str = None) -> Optional[Dict]:
        """Find patient by name and optionally DOB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if dob:
            cursor.execute('''
                SELECT * FROM patients 
                WHERE first_name = ? AND last_name = ? AND date_of_birth = ?
            ''', (first_name, last_name, dob))
        else:
            cursor.execute('''
                SELECT * FROM patients 
                WHERE first_name = ? AND last_name = ?
            ''', (first_name, last_name))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_available_slots(self, doctor_name: str = None, date: str = None) -> List[Dict]:
        """Get available appointment slots"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM doctor_schedules 
            WHERE is_available = 1
        '''
        params = []
        
        if doctor_name:
            query += ' AND doctor_name = ?'
            params.append(doctor_name)
        
        if date:
            query += ' AND date = ?'
            params.append(date)
        
        query += ' ORDER BY date, start_time'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def book_appointment(self, patient_id: str, doctor_name: str, 
                        appointment_date: str, start_time: str, 
                        duration: int, reason: str = None) -> str:
        """Book an appointment"""
        appointment_id = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate end time
        start_dt = datetime.strptime(f"{appointment_date} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=duration)
        end_time = end_dt.strftime("%H:%M")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert appointment
        cursor.execute('''
            INSERT INTO appointments 
            (appointment_id, patient_id, doctor_name, appointment_date, 
             start_time, end_time, duration, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, doctor_name, appointment_date,
              start_time, end_time, duration, reason))
        
        # Mark slot as unavailable
        cursor.execute('''
            UPDATE doctor_schedules 
            SET is_available = 0 
            WHERE doctor_name = ? AND date = ? AND start_time = ?
        ''', (doctor_name, appointment_date, start_time))
        
        conn.commit()
        conn.close()
        
        return appointment_id
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict]:
        """Get appointment details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, p.first_name, p.last_name, p.email, p.phone
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.appointment_id = ?
        ''', (appointment_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def schedule_reminder(self, appointment_id: str, reminder_type: str, 
                         scheduled_time: str) -> int:
        """Schedule a reminder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders (appointment_id, reminder_type, scheduled_time)
            VALUES (?, ?, ?)
        ''', (appointment_id, reminder_type, scheduled_time))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reminder_id
    
    def send_form(self, appointment_id: str, form_type: str) -> int:
        """Record form sending"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO forms (appointment_id, form_type)
            VALUES (?, ?)
        ''', (appointment_id, form_type))
        
        form_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return form_id
    
    def get_appointments_for_export(self) -> pd.DataFrame:
        """Get all appointments for Excel export"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                a.appointment_id,
                p.first_name,
                p.last_name,
                p.phone,
                p.email,
                a.doctor_name,
                a.appointment_date,
                a.start_time,
                a.end_time,
                a.duration,
                a.status,
                a.reason,
                a.created_at
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            ORDER BY a.appointment_date, a.start_time
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def find_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Find patient by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
            conn.close()
            return result
        conn.close()
        return None

# Initialize database and load sample data
def initialize_database():
    """Initialize database with sample data"""
    db = MedicalDatabase()
    
    # Load sample data if files exist
    if os.path.exists("data/patients.csv"):
        db.load_patients_from_csv("data/patients.csv")
    
    if os.path.exists("data/doctor_schedules.xlsx"):
        db.load_schedules_from_excel("data/doctor_schedules.xlsx")
    
    return db

if __name__ == "__main__":
    # Generate sample data first
    from data_generator import create_sample_data
    create_sample_data()
    
    # Initialize database
    db = initialize_database()
    print("Database initialized successfully!")
