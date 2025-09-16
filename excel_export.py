import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Optional
from database import MedicalDatabase

class ExcelExporter:
    """Handle Excel export functionality for appointments and reports"""
    
    def __init__(self, db: MedicalDatabase):
        self.db = db
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_appointments(self, filename: str = None) -> str:
        """Export all appointments to Excel"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"appointments_export_{timestamp}.xlsx"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Get appointments data
        appointments_df = self.db.get_appointments_for_export()
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Write appointments sheet
            appointments_df.to_excel(writer, sheet_name='Appointments', index=False)
            
            # Create summary sheet
            summary_data = self._create_summary_data(appointments_df)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create doctor schedule sheet
            schedule_data = self._create_schedule_data()
            schedule_df = pd.DataFrame(schedule_data)
            schedule_df.to_excel(writer, sheet_name='Doctor_Schedules', index=False)
        
        print(f"Appointments exported to {filepath}")
        return filepath
    
    def export_daily_appointments(self, date: str) -> str:
        """Export appointments for a specific date"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_appointments_{date}_{timestamp}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        # Get appointments for specific date
        appointments_df = self.db.get_appointments_for_export()
        
        # Debug: Print what we're looking for
        print(f"Looking for appointments on date: {date}")
        print(f"Available dates in database: {appointments_df['appointment_date'].unique() if not appointments_df.empty else 'No appointments'}")
        
        if not appointments_df.empty:
            # Convert appointment_date to string for comparison
            appointments_df['appointment_date'] = appointments_df['appointment_date'].astype(str)
            daily_appointments = appointments_df[appointments_df['appointment_date'] == date]
        else:
            daily_appointments = pd.DataFrame()
        
        if daily_appointments.empty:
            print(f"No appointments found for {date}")
            # Create an empty Excel file with a message
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                empty_df = pd.DataFrame({'Message': [f'No appointments found for {date}']})
                empty_df.to_excel(writer, sheet_name=f'Appointments_{date}', index=False)
            return filepath
        
        # Create Excel file
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            daily_appointments.to_excel(writer, sheet_name=f'Appointments_{date}', index=False)
            
            # Create time slots summary
            time_slots = self._create_time_slots_summary(daily_appointments)
            time_slots_df = pd.DataFrame(time_slots)
            time_slots_df.to_excel(writer, sheet_name='Time_Slots', index=False)
        
        print(f"Daily appointments for {date} exported to {filepath}")
        return filepath
    
    def export_doctor_schedule(self, doctor_name: str, start_date: str, end_date: str) -> str:
        """Export doctor's schedule for a date range"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"doctor_schedule_{doctor_name.replace(' ', '_')}_{start_date}_{timestamp}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        # Get doctor's schedule
        conn = self.db.db_path
        # This would need proper database implementation
        # For now, we'll create a sample schedule
        
        schedule_data = self._create_doctor_schedule_data(doctor_name, start_date, end_date)
        schedule_df = pd.DataFrame(schedule_data)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            schedule_df.to_excel(writer, sheet_name='Doctor_Schedule', index=False)
            
            # Create availability summary
            availability = self._create_availability_summary(schedule_df)
            availability_df = pd.DataFrame(availability)
            availability_df.to_excel(writer, sheet_name='Availability', index=False)
        
        print(f"Doctor schedule for {doctor_name} exported to {filepath}")
        return filepath
    
    def export_patient_report(self, patient_id: str) -> str:
        """Export patient's appointment history"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"patient_report_{patient_id}_{timestamp}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        # Get patient's appointments
        appointments_df = self.db.get_appointments_for_export()
        patient_appointments = appointments_df[appointments_df['patient_id'] == patient_id]
        
        if patient_appointments.empty:
            print(f"No appointments found for patient {patient_id}")
            return None
        
        # Get patient info
        patient_info = self.db.find_patient_by_id(patient_id)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Patient information sheet
            if patient_info:
                patient_df = pd.DataFrame([patient_info])
                patient_df.to_excel(writer, sheet_name='Patient_Info', index=False)
            
            # Appointment history sheet
            patient_appointments.to_excel(writer, sheet_name='Appointment_History', index=False)
            
            # Create summary statistics
            summary_stats = self._create_patient_summary_stats(patient_appointments)
            summary_df = pd.DataFrame([summary_stats])
            summary_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
        
        print(f"Patient report for {patient_id} exported to {filepath}")
        return filepath
    
    def _create_summary_data(self, appointments_df: pd.DataFrame) -> List[Dict]:
        """Create summary data for appointments"""
        
        total_appointments = len(appointments_df)
        new_patients = len(appointments_df[appointments_df['duration'] == 60])
        returning_patients = len(appointments_df[appointments_df['duration'] == 30])
        
        # Group by doctor
        doctor_counts = appointments_df['doctor_name'].value_counts().to_dict()
        
        # Group by date
        date_counts = appointments_df['appointment_date'].value_counts().to_dict()
        
        summary_data = [
            {"Metric": "Total Appointments", "Value": total_appointments},
            {"Metric": "New Patients", "Value": new_patients},
            {"Metric": "Returning Patients", "Value": returning_patients},
            {"Metric": "Average Appointments per Day", "Value": len(date_counts)},
        ]
        
        # Add doctor breakdown
        for doctor, count in doctor_counts.items():
            summary_data.append({"Metric": f"Appointments with {doctor}", "Value": count})
        
        return summary_data
    
    def _create_schedule_data(self) -> List[Dict]:
        """Create doctor schedule data"""
        
        # This would query the actual database
        # For now, return sample data
        return [
            {
                "Doctor": "Dr. Sarah Johnson",
                "Date": "2024-01-15",
                "Start_Time": "09:00",
                "End_Time": "17:00",
                "Available_Slots": 16,
                "Booked_Slots": 12,
                "Utilization": "75%"
            },
            {
                "Doctor": "Dr. Michael Chen",
                "Date": "2024-01-15",
                "Start_Time": "09:00",
                "End_Time": "17:00",
                "Available_Slots": 16,
                "Booked_Slots": 14,
                "Utilization": "87.5%"
            }
        ]
    
    def _create_time_slots_summary(self, appointments_df: pd.DataFrame) -> List[Dict]:
        """Create time slots summary for daily appointments"""
        
        time_slots = []
        for hour in range(9, 17):  # 9 AM to 5 PM
            for minute in [0, 30]:  # Every 30 minutes
                time_str = f"{hour:02d}:{minute:02d}"
                slot_appointments = appointments_df[appointments_df['start_time'] == time_str]
                
                time_slots.append({
                    "Time_Slot": time_str,
                    "Appointments": len(slot_appointments),
                    "Doctors": ", ".join(slot_appointments['doctor_name'].unique()) if not slot_appointments.empty else "None"
                })
        
        return time_slots
    
    def _create_doctor_schedule_data(self, doctor_name: str, start_date: str, end_date: str) -> List[Dict]:
        """Create doctor schedule data for date range"""
        
        # This would query the actual database
        # For now, return sample data
        schedule_data = []
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        current_dt = start_dt
        while current_dt <= end_dt:
            if current_dt.weekday() < 5:  # Weekdays only
                for hour in range(9, 17):
                    for minute in [0, 30]:
                        schedule_data.append({
                            "Date": current_dt.strftime("%Y-%m-%d"),
                            "Start_Time": f"{hour:02d}:{minute:02d}",
                            "End_Time": f"{hour:02d}:{(minute + 30) % 60:02d}",
                            "Available": "Yes" if (hour + minute/60) % 2 == 0 else "No"
                        })
            current_dt += timedelta(days=1)
        
        return schedule_data
    
    def _create_availability_summary(self, schedule_df: pd.DataFrame) -> List[Dict]:
        """Create availability summary for doctor schedule"""
        
        total_slots = len(schedule_df)
        available_slots = len(schedule_df[schedule_df['Available'] == 'Yes'])
        booked_slots = total_slots - available_slots
        
        return [
            {"Metric": "Total Time Slots", "Value": total_slots},
            {"Metric": "Available Slots", "Value": available_slots},
            {"Metric": "Booked Slots", "Value": booked_slots},
            {"Metric": "Utilization Rate", "Value": f"{(booked_slots/total_slots)*100:.1f}%"}
        ]
    
    def _create_patient_summary_stats(self, patient_appointments: pd.DataFrame) -> Dict:
        """Create summary statistics for patient"""
        
        total_appointments = len(patient_appointments)
        unique_doctors = patient_appointments['doctor_name'].nunique()
        first_appointment = patient_appointments['appointment_date'].min()
        last_appointment = patient_appointments['appointment_date'].max()
        
        return {
            "Total_Appointments": total_appointments,
            "Unique_Doctors_Seen": unique_doctors,
            "First_Appointment": first_appointment,
            "Last_Appointment": last_appointment,
            "Average_Appointments_per_Month": total_appointments / max(1, (datetime.now() - datetime.strptime(first_appointment, "%Y-%m-%d")).days / 30)
        }

class ReportGenerator:
    """Generate various reports for the medical appointment system"""
    
    def __init__(self, db: MedicalDatabase):
        self.db = db
        self.exporter = ExcelExporter(db)
    
    def generate_daily_report(self, date: str) -> str:
        """Generate daily appointment report"""
        
        return self.exporter.export_daily_appointments(date)
    
    def generate_weekly_report(self, start_date: str) -> str:
        """Generate weekly appointment report"""
        
        # Calculate end date (7 days later)
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=6)
        end_date = end_dt.strftime("%Y-%m-%d")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weekly_report_{start_date}_to_{end_date}_{timestamp}.xlsx"
        filepath = os.path.join(self.exporter.export_dir, filename)
        
        # Get appointments for the week
        appointments_df = self.db.get_appointments_for_export()
        weekly_appointments = appointments_df[
            (appointments_df['appointment_date'] >= start_date) & 
            (appointments_df['appointment_date'] <= end_date)
        ]
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Weekly appointments
            weekly_appointments.to_excel(writer, sheet_name='Weekly_Appointments', index=False)
            
            # Daily breakdown
            daily_breakdown = weekly_appointments.groupby('appointment_date').size().reset_index(name='Appointment_Count')
            daily_breakdown.to_excel(writer, sheet_name='Daily_Breakdown', index=False)
            
            # Doctor breakdown
            doctor_breakdown = weekly_appointments.groupby('doctor_name').size().reset_index(name='Appointment_Count')
            doctor_breakdown.to_excel(writer, sheet_name='Doctor_Breakdown', index=False)
        
        print(f"Weekly report for {start_date} to {end_date} exported to {filepath}")
        return filepath
    
    def generate_monthly_report(self, year: int, month: int) -> str:
        """Generate monthly appointment report"""
        
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monthly_report_{year}_{month:02d}_{timestamp}.xlsx"
        filepath = os.path.join(self.exporter.export_dir, filename)
        
        # Get appointments for the month
        appointments_df = self.db.get_appointments_for_export()
        monthly_appointments = appointments_df[
            (appointments_df['appointment_date'] >= start_date) & 
            (appointments_df['appointment_date'] < end_date)
        ]
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Monthly appointments
            monthly_appointments.to_excel(writer, sheet_name='Monthly_Appointments', index=False)
            
            # Weekly breakdown
            monthly_appointments['week'] = pd.to_datetime(monthly_appointments['appointment_date']).dt.isocalendar().week
            weekly_breakdown = monthly_appointments.groupby('week').size().reset_index(name='Appointment_Count')
            weekly_breakdown.to_excel(writer, sheet_name='Weekly_Breakdown', index=False)
            
            # Doctor performance
            doctor_performance = monthly_appointments.groupby('doctor_name').agg({
                'appointment_id': 'count',
                'duration': 'sum'
            }).reset_index()
            doctor_performance.columns = ['Doctor', 'Total_Appointments', 'Total_Minutes']
            doctor_performance.to_excel(writer, sheet_name='Doctor_Performance', index=False)
        
        print(f"Monthly report for {year}-{month:02d} exported to {filepath}")
        return filepath
