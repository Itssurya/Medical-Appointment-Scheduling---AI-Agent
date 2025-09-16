"""
Simplified Medical Appointment Agent for Demo
This version doesn't require complex LangGraph setup
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from database import MedicalDatabase

class SimpleAppointmentAgent:
    """Simplified appointment booking agent"""
    
    def __init__(self):
        self.db = MedicalDatabase()
        self.current_step = "greeting"
        self.patient_info = {}
        self.appointment_details = {}
        self.conversation_history = []
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process user message and return response"""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        if self.current_step == "greeting":
            return self._handle_greeting(user_input)
        elif self.current_step == "patient_lookup":
            return self._handle_patient_lookup()
        elif self.current_step == "scheduling":
            return self._handle_scheduling(user_input)
        elif self.current_step == "insurance_collection":
            return self._handle_insurance_collection(user_input)
        elif self.current_step == "confirmation":
            return self._handle_confirmation()
        else:
            return {"message": "I'm not sure how to help with that. Let me start over.", "next_step": "greeting"}
    
    def _handle_greeting(self, user_input: str) -> Dict[str, Any]:
        """Handle initial greeting and data collection"""
        
        # Extract patient information
        self._extract_patient_info(user_input)
        
        # Check if we have required information
        required_fields = ["first_name", "last_name", "date_of_birth"]
        missing_fields = [field for field in required_fields if field not in self.patient_info]
        
        if missing_fields:
            if "first_name" not in self.patient_info:
                message = "Hello! I'd be happy to help you schedule an appointment. Could you please provide your first and last name?"
            elif "last_name" not in self.patient_info:
                message = "Thank you! Could you also provide your last name?"
            elif "date_of_birth" not in self.patient_info:
                message = "Perfect! Could you also provide your date of birth (MM/DD/YYYY format)?"
            else:
                message = f"I still need: {', '.join(missing_fields)}"
        else:
            message = "Thank you! I have all the information I need. Let me look up your records."
            self.current_step = "patient_lookup"
        
        # Debug: Show what we extracted
        if self.patient_info:
            print(f"DEBUG: Extracted patient info: {self.patient_info}")
        
        self.conversation_history.append({"role": "assistant", "content": message})
        return {"message": message, "next_step": self.current_step}
    
    def _handle_patient_lookup(self) -> Dict[str, Any]:
        """Handle patient lookup in database"""
        
        # Search for patient
        patient = self.db.find_patient(
            self.patient_info.get("first_name", ""),
            self.patient_info.get("last_name", ""),
            self.patient_info.get("date_of_birth")
        )
        
        if patient:
            # Update patient info with found data
            self.patient_info.update(patient)
            self.patient_info["is_new_patient"] = False
            message = f"Welcome back, {patient['first_name']}! I found your records. You're a returning patient."
        else:
            self.patient_info["is_new_patient"] = True
            message = f"Hello {self.patient_info.get('first_name', 'there')}! I don't see you in our system, so you'll be a new patient."
        
        self.current_step = "scheduling"
        self.conversation_history.append({"role": "assistant", "content": message})
        return {"message": message, "next_step": self.current_step}
    
    def _handle_scheduling(self, user_input: str) -> Dict[str, Any]:
        """Handle appointment scheduling"""
        
        # Get available slots
        available_slots = self.db.get_available_slots()
        
        if not available_slots:
            message = "I'm sorry, but there are no available appointments at the moment. Please try again later."
            self.conversation_history.append({"role": "assistant", "content": message})
            return {"message": message, "next_step": self.current_step}
        
        # Check if user is selecting a slot
        if user_input.isdigit():
            selection = int(user_input) - 1
            if 0 <= selection < len(available_slots):
                selected_slot = available_slots[selection]
                
                # Book appointment
                duration = 60 if self.patient_info.get("is_new_patient") else 30
                appointment_id = self.db.book_appointment(
                    patient_id=self.patient_info.get("patient_id", "NEW001"),
                    doctor_name=selected_slot["doctor_name"],
                    appointment_date=selected_slot["date"],
                    start_time=selected_slot["start_time"],
                    duration=duration,
                    reason="Routine appointment"
                )
                
                self.appointment_details = {
                    "appointment_id": appointment_id,
                    "doctor_name": selected_slot["doctor_name"],
                    "date": selected_slot["date"],
                    "start_time": selected_slot["start_time"],
                    "duration": duration
                }
                
                message = f"Perfect! I've scheduled your appointment for {selected_slot['date']} at {selected_slot['start_time']} with {selected_slot['doctor_name']}. Your appointment ID is {appointment_id}."
                self.current_step = "insurance_collection"
            else:
                message = "That's not a valid selection. Please choose from the available options."
        else:
            # Show available slots
            duration = 60 if self.patient_info.get("is_new_patient") else 30
            slots_text = f"I can schedule you for a {duration}-minute appointment. Here are the available slots:\n"
            for i, slot in enumerate(available_slots[:5]):
                slots_text += f"{i+1}. {slot['date']} at {slot['start_time']} with {slot['doctor_name']} ({slot['specialty']})\n"
            slots_text += "\nPlease select a number from the options above."
            message = slots_text
        
        self.conversation_history.append({"role": "assistant", "content": message})
        return {"message": message, "next_step": self.current_step}
    
    def _handle_insurance_collection(self, user_input: str) -> Dict[str, Any]:
        """Handle insurance information collection"""
        
        # Extract insurance information
        self._extract_insurance_info(user_input)
        
        # Check if we have insurance info
        if "insurance_carrier" not in self.patient_info:
            message = "I need to collect your insurance information. What insurance carrier do you have?"
        elif "member_id" not in self.patient_info:
            message = "Thank you. What's your member ID?"
        else:
            message = "Perfect! I have all the information I need. Let me confirm your appointment details."
            self.current_step = "confirmation"
        
        self.conversation_history.append({"role": "assistant", "content": message})
        return {"message": message, "next_step": self.current_step}
    
    def _handle_confirmation(self) -> Dict[str, Any]:
        """Handle final confirmation"""
        
        appointment_details = self.appointment_details
        patient_info = self.patient_info
        
        message = f"""
        Appointment Confirmed! 🎉
        
        Patient: {patient_info['first_name']} {patient_info['last_name']}
        Doctor: {appointment_details['doctor_name']}
        Date: {appointment_details['date']}
        Time: {appointment_details['start_time']}
        Duration: {appointment_details['duration']} minutes
        Appointment ID: {appointment_details['appointment_id']}
        
        I'll send you intake forms via email shortly. You'll also receive reminder notifications before your appointment.
        """
        
        # Schedule reminders
        appointment_datetime = datetime.strptime(
            f"{appointment_details['date']} {appointment_details['start_time']}", 
            "%Y-%m-%d %H:%M"
        )
        
        # Schedule 3 reminders
        reminders = [
            (appointment_datetime - timedelta(hours=24), "24_hour_reminder"),
            (appointment_datetime - timedelta(hours=2), "2_hour_reminder"),
            (appointment_datetime - timedelta(hours=1), "1_hour_reminder")
        ]
        
        for reminder_time, reminder_type in reminders:
            self.db.schedule_reminder(
                appointment_details["appointment_id"],
                reminder_type,
                reminder_time.strftime("%Y-%m-%d %H:%M")
            )
        
        self.conversation_history.append({"role": "assistant", "content": message})
        return {"message": message, "next_step": "completed", "completed": True}
    
    def _extract_patient_info(self, user_input: str):
        """Extract patient information from user input"""
        
        # Extract name - multiple patterns
        name_patterns = [
            r"my name is (\w+)\s+(\w+)",
            r"first and last name is (\w+)\s+(\w+)",
            r"name is (\w+)\s+(\w+)",
            r"i'm (\w+)\s+(\w+)",
            r"i am (\w+)\s+(\w+)",
            r"(\w+)\s+(\w+)"  # Simple two words pattern
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, user_input.lower())
            if name_match:
                self.patient_info["first_name"] = name_match.group(1).title()
                self.patient_info["last_name"] = name_match.group(2).title()
                break
        
        # Extract date of birth
        dob_patterns = [
            r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})",
            r"(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})"
        ]
        for pattern in dob_patterns:
            dob_match = re.search(pattern, user_input)
            if dob_match:
                groups = dob_match.groups()
                if len(groups[0]) == 4:  # YYYY-MM-DD format
                    self.patient_info["date_of_birth"] = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                else:  # MM/DD/YYYY format
                    self.patient_info["date_of_birth"] = f"{groups[2]}-{groups[0].zfill(2)}-{groups[1].zfill(2)}"
                break
        
        # Extract phone number
        phone_pattern = r"(\d{3})[-\s]?(\d{3})[-\s]?(\d{4})"
        phone_match = re.search(phone_pattern, user_input)
        if phone_match:
            self.patient_info["phone"] = f"{phone_match.group(1)}-{phone_match.group(2)}-{phone_match.group(3)}"
        
        # Extract email
        email_pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        email_match = re.search(email_pattern, user_input)
        if email_match:
            self.patient_info["email"] = email_match.group(1)
    
    def _extract_insurance_info(self, user_input: str):
        """Extract insurance information from user input"""
        
        # Common insurance carriers
        carriers = ["Blue Cross", "Aetna", "Cigna", "UnitedHealth", "Humana", "Kaiser", "Anthem"]
        
        for carrier in carriers:
            if carrier.lower() in user_input.lower():
                self.patient_info["insurance_carrier"] = carrier
                break
        
        # Extract member ID
        member_id_pattern = r"member\s*id[:\s]*([A-Z0-9]+)"
        member_match = re.search(member_id_pattern, user_input, re.IGNORECASE)
        if member_match:
            self.patient_info["member_id"] = member_match.group(1)
    
    def reset(self):
        """Reset the agent state"""
        self.current_step = "greeting"
        self.patient_info = {}
        self.appointment_details = {}
        self.conversation_history = []
