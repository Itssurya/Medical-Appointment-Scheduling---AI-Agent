import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from twilio.rest import Client
from config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
)

class EmailService:
    """Email service for sending appointment confirmations and forms"""
    
    def __init__(self):
        self.smtp_server = EMAIL_HOST
        self.smtp_port = EMAIL_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
    
    def send_appointment_confirmation(self, patient_email: str, appointment_details: Dict) -> bool:
        """Send appointment confirmation email"""
        
        subject = f"Appointment Confirmation - {appointment_details['date']}"
        
        body = f"""
        Dear {appointment_details.get('patient_name', 'Patient')},
        
        Your appointment has been confirmed with the following details:
        
        Appointment ID: {appointment_details['appointment_id']}
        Doctor: {appointment_details['doctor_name']}
        Date: {appointment_details['date']}
        Time: {appointment_details['start_time']}
        Duration: {appointment_details['duration']} minutes
        
        Please arrive 15 minutes early for your appointment.
        
        If you need to reschedule or cancel, please contact us at least 24 hours in advance.
        
        Best regards,
        Medical Appointment System
        """
        
        return self._send_email(patient_email, subject, body)
    
    def send_intake_forms(self, patient_email: str, form_type: str, appointment_details: Dict) -> bool:
        """Send intake forms via email"""
        
        subject = f"Intake Forms - {appointment_details['date']} Appointment"
        
        if form_type == "new_patient_form":
            body = f"""
            Dear {appointment_details.get('patient_name', 'Patient')},
            
            Please complete the attached new patient intake forms before your appointment on {appointment_details['date']} at {appointment_details['start_time']}.
            
            The forms include:
            - Medical History
            - Current Medications
            - Allergies
            - Emergency Contact Information
            - Insurance Information
            - Previous Medical Records
            
            Please fill out these forms and bring them to your appointment, or complete them online if available.
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            Medical Appointment System
            """
        else:  # returning_patient_form
            body = f"""
            Dear {appointment_details.get('patient_name', 'Patient')},
            
            Please complete the attached returning patient update forms before your appointment on {appointment_details['date']} at {appointment_details['start_time']}.
            
            The forms include:
            - Updated Medical History
            - Current Medications
            - New Allergies
            - Insurance Updates
            - Reason for Visit
            
            Please fill out these forms and bring them to your appointment, or complete them online if available.
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            Medical Appointment System
            """
        
        return self._send_email(patient_email, subject, body)
    
    def send_reminder(self, patient_email: str, appointment_details: Dict, reminder_type: str) -> bool:
        """Send appointment reminder email"""
        
        if reminder_type == "24_hour_reminder":
            subject = "Appointment Reminder - Tomorrow"
            body = f"""
            Dear {appointment_details.get('patient_name', 'Patient')},
            
            This is a friendly reminder that you have an appointment tomorrow:
            
            Date: {appointment_details['date']}
            Time: {appointment_details['start_time']}
            Doctor: {appointment_details['doctor_name']}
            
            Please arrive 15 minutes early.
            
            If you need to reschedule, please contact us as soon as possible.
            
            Best regards,
            Medical Appointment System
            """
        
        elif reminder_type == "2_hour_reminder":
            subject = "Appointment Reminder - 2 Hours"
            body = f"""
            Dear {appointment_details.get('patient_name', 'Patient')},
            
            This is a reminder that you have an appointment in 2 hours:
            
            Date: {appointment_details['date']}
            Time: {appointment_details['start_time']}
            Doctor: {appointment_details['doctor_name']}
            
            Please confirm you're still coming by replying to this email.
            
            Best regards,
            Medical Appointment System
            """
        
        elif reminder_type == "1_hour_reminder":
            subject = "Appointment Reminder - 1 Hour"
            body = f"""
            Dear {appointment_details.get('patient_name', 'Patient')},
            
            This is a final reminder that you have an appointment in 1 hour:
            
            Date: {appointment_details['date']}
            Time: {appointment_details['start_time']}
            Doctor: {appointment_details['doctor_name']}
            
            If you're running late, please call us immediately.
            
            Best regards,
            Medical Appointment System
            """
        
        else:
            return False
        
        return self._send_email(patient_email, subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

class SMSService:
    """SMS service for sending appointment reminders"""
    
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.from_number = TWILIO_PHONE_NUMBER
    
    def send_appointment_confirmation(self, patient_phone: str, appointment_details: Dict) -> bool:
        """Send appointment confirmation SMS"""
        
        message = f"""
        Appointment Confirmed!
        Dr: {appointment_details['doctor_name']}
        Date: {appointment_details['date']}
        Time: {appointment_details['start_time']}
        ID: {appointment_details['appointment_id']}
        """
        
        return self._send_sms(patient_phone, message)
    
    def send_reminder(self, patient_phone: str, appointment_details: Dict, reminder_type: str) -> bool:
        """Send appointment reminder SMS"""
        
        if reminder_type == "24_hour_reminder":
            message = f"""
            Reminder: You have an appointment tomorrow at {appointment_details['start_time']} with {appointment_details['doctor_name']}.
            Please arrive 15 minutes early.
            """
        
        elif reminder_type == "2_hour_reminder":
            message = f"""
            Reminder: You have an appointment in 2 hours at {appointment_details['start_time']} with {appointment_details['doctor_name']}.
            Please confirm you're still coming.
            """
        
        elif reminder_type == "1_hour_reminder":
            message = f"""
            Final reminder: You have an appointment in 1 hour at {appointment_details['start_time']} with {appointment_details['doctor_name']}.
            If running late, please call us.
            """
        
        else:
            return False
        
        return self._send_sms(patient_phone, message)
    
    def _send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS using Twilio"""
        try:
            # Format phone number (assuming US format)
            if not to_phone.startswith('+1'):
                to_phone = f"+1{to_phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')}"
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )
            
            print(f"SMS sent successfully to {to_phone}: {message_obj.sid}")
            return True
            
        except Exception as e:
            print(f"Failed to send SMS to {to_phone}: {str(e)}")
            return False

class ReminderScheduler:
    """Scheduler for automated reminders"""
    
    def __init__(self, db, email_service: EmailService, sms_service: SMSService):
        self.db = db
        self.email_service = email_service
        self.sms_service = sms_service
    
    def process_pending_reminders(self):
        """Process all pending reminders"""
        
        # Get all pending reminders
        conn = self.db.db_path
        # This would need to be implemented with proper database queries
        # For now, we'll simulate the reminder processing
        
        print("Processing pending reminders...")
        
        # In a real implementation, you would:
        # 1. Query the database for pending reminders
        # 2. Check if it's time to send them
        # 3. Send the reminders
        # 4. Update the reminder status
        
        return True
    
    def send_reminder(self, appointment_id: str, reminder_type: str):
        """Send a specific reminder"""
        
        # Get appointment details
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            print(f"Appointment {appointment_id} not found")
            return False
        
        # Send email reminder
        email_sent = self.email_service.send_reminder(
            appointment['email'],
            appointment,
            reminder_type
        )
        
        # Send SMS reminder
        sms_sent = self.sms_service.send_reminder(
            appointment['phone'],
            appointment,
            reminder_type
        )
        
        # Update reminder status in database
        # This would need to be implemented with proper database updates
        
        return email_sent or sms_sent

class FormGenerator:
    """Generate intake forms for patients"""
    
    def __init__(self):
        self.templates_dir = "templates"
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def generate_new_patient_form(self, patient_info: Dict) -> str:
        """Generate new patient intake form"""
        
        form_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>New Patient Intake Form</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; }}
                .field {{ margin: 10px 0; }}
                label {{ display: block; font-weight: bold; }}
                input, textarea {{ width: 100%; padding: 5px; margin: 5px 0; }}
                .required {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>New Patient Intake Form</h1>
                <p>Patient: {patient_info.get('first_name', '')} {patient_info.get('last_name', '')}</p>
                <p>Date of Birth: {patient_info.get('date_of_birth', '')}</p>
            </div>
            
            <div class="section">
                <h2>Medical History</h2>
                <div class="field">
                    <label>Previous surgeries or hospitalizations:</label>
                    <textarea rows="3" name="previous_surgeries"></textarea>
                </div>
                <div class="field">
                    <label>Current medical conditions:</label>
                    <textarea rows="3" name="current_conditions"></textarea>
                </div>
                <div class="field">
                    <label>Family medical history:</label>
                    <textarea rows="3" name="family_history"></textarea>
                </div>
            </div>
            
            <div class="section">
                <h2>Current Medications</h2>
                <div class="field">
                    <label>List all current medications (name, dosage, frequency):</label>
                    <textarea rows="4" name="medications"></textarea>
                </div>
                <div class="field">
                    <label>Allergies to medications:</label>
                    <textarea rows="2" name="medication_allergies"></textarea>
                </div>
            </div>
            
            <div class="section">
                <h2>Emergency Contact</h2>
                <div class="field">
                    <label>Name: <span class="required">*</span></label>
                    <input type="text" name="emergency_contact_name" required>
                </div>
                <div class="field">
                    <label>Phone: <span class="required">*</span></label>
                    <input type="tel" name="emergency_contact_phone" required>
                </div>
                <div class="field">
                    <label>Relationship:</label>
                    <input type="text" name="emergency_contact_relationship">
                </div>
            </div>
            
            <div class="section">
                <h2>Insurance Information</h2>
                <div class="field">
                    <label>Insurance Carrier: <span class="required">*</span></label>
                    <input type="text" name="insurance_carrier" required>
                </div>
                <div class="field">
                    <label>Member ID: <span class="required">*</span></label>
                    <input type="text" name="member_id" required>
                </div>
                <div class="field">
                    <label>Group Number:</label>
                    <input type="text" name="group_number">
                </div>
            </div>
            
            <div class="section">
                <h2>Additional Information</h2>
                <div class="field">
                    <label>Reason for today's visit:</label>
                    <textarea rows="3" name="visit_reason"></textarea>
                </div>
                <div class="field">
                    <label>Any questions or concerns:</label>
                    <textarea rows="3" name="questions_concerns"></textarea>
                </div>
            </div>
        </body>
        </html>
        """
        
        return form_html
    
    def generate_returning_patient_form(self, patient_info: Dict) -> str:
        """Generate returning patient update form"""
        
        form_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Returning Patient Update Form</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; }}
                .field {{ margin: 10px 0; }}
                label {{ display: block; font-weight: bold; }}
                input, textarea {{ width: 100%; padding: 5px; margin: 5px 0; }}
                .required {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Returning Patient Update Form</h1>
                <p>Patient: {patient_info.get('first_name', '')} {patient_info.get('last_name', '')}</p>
                <p>Date of Birth: {patient_info.get('date_of_birth', '')}</p>
            </div>
            
            <div class="section">
                <h2>Updated Medical History</h2>
                <div class="field">
                    <label>Any changes to your medical conditions since your last visit:</label>
                    <textarea rows="3" name="updated_conditions"></textarea>
                </div>
                <div class="field">
                    <label>New medications or changes to existing medications:</label>
                    <textarea rows="3" name="medication_changes"></textarea>
                </div>
                <div class="field">
                    <label>New allergies:</label>
                    <textarea rows="2" name="new_allergies"></textarea>
                </div>
            </div>
            
            <div class="section">
                <h2>Insurance Updates</h2>
                <div class="field">
                    <label>Has your insurance changed?</label>
                    <input type="radio" name="insurance_changed" value="yes"> Yes
                    <input type="radio" name="insurance_changed" value="no"> No
                </div>
                <div class="field">
                    <label>If yes, please provide new insurance information:</label>
                    <textarea rows="3" name="new_insurance_info"></textarea>
                </div>
            </div>
            
            <div class="section">
                <h2>Reason for Today's Visit</h2>
                <div class="field">
                    <label>What brings you in today?</label>
                    <textarea rows="3" name="visit_reason" required></textarea>
                </div>
                <div class="field">
                    <label>Any specific symptoms or concerns?</label>
                    <textarea rows="3" name="symptoms_concerns"></textarea>
                </div>
            </div>
        </body>
        </html>
        """
        
        return form_html
    
    def save_form(self, form_html: str, filename: str):
        """Save form to file"""
        
        filepath = os.path.join(self.templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(form_html)
        
        return filepath
