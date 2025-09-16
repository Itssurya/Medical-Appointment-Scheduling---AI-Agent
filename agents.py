from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from database import MedicalDatabase
from config import OPENAI_API_KEY, NEW_PATIENT_DURATION, RETURNING_PATIENT_DURATION

class AppointmentState:
    """State management for appointment booking workflow"""
    def __init__(self):
        self.patient_info = {}
        self.appointment_details = {}
        self.insurance_info = {}
        self.current_step = "greeting"
        self.conversation_history = []
        self.errors = []
        self.completed = False

class PatientGreetingAgent:
    """Agent responsible for initial patient greeting and data collection"""
    
    def __init__(self, llm):
        self.llm = llm
        self.required_fields = ["first_name", "last_name", "date_of_birth"]
        self.optional_fields = ["phone", "email", "preferred_doctor"]
    
    def greet_and_collect_info(self, state: AppointmentState, user_input: str) -> Dict[str, Any]:
        """Greet patient and collect basic information"""
        
        # Add user input to conversation history
        state.conversation_history.append({"role": "user", "content": user_input})
        
        # Check if we have all required information
        missing_fields = [field for field in self.required_fields if field not in state.patient_info]
        
        if not missing_fields:
            return {
                "next_step": "patient_lookup",
                "message": "Thank you! I have all the information I need. Let me look up your records.",
                "patient_info": state.patient_info
            }
        
        # Generate response based on missing information
        system_prompt = f"""
        You are a friendly medical appointment scheduling assistant. 
        You need to collect the following information from the patient:
        Required: {', '.join(self.required_fields)}
        Optional: {', '.join(self.optional_fields)}
        
        Current information collected: {state.patient_info}
        Missing required fields: {missing_fields}
        
        Be conversational and helpful. Ask for one piece of information at a time.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        response = self.llm.invoke(messages)
        
        # Extract information from user input
        self._extract_patient_info(user_input, state)
        
        # Add assistant response to conversation history
        state.conversation_history.append({"role": "assistant", "content": response.content})
        
        return {
            "next_step": "greeting" if missing_fields else "patient_lookup",
            "message": response.content,
            "patient_info": state.patient_info
        }
    
    def _extract_patient_info(self, user_input: str, state: AppointmentState):
        """Extract patient information from user input using NLP"""
        
        # Extract name (simple pattern matching)
        name_pattern = r"my name is (\w+)\s+(\w+)"
        name_match = re.search(name_pattern, user_input.lower())
        if name_match:
            state.patient_info["first_name"] = name_match.group(1).title()
            state.patient_info["last_name"] = name_match.group(2).title()
        
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
                    state.patient_info["date_of_birth"] = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                else:  # MM/DD/YYYY format
                    state.patient_info["date_of_birth"] = f"{groups[2]}-{groups[0].zfill(2)}-{groups[1].zfill(2)}"
                break
        
        # Extract phone number
        phone_pattern = r"(\d{3})[-\s]?(\d{3})[-\s]?(\d{4})"
        phone_match = re.search(phone_pattern, user_input)
        if phone_match:
            state.patient_info["phone"] = f"{phone_match.group(1)}-{phone_match.group(2)}-{phone_match.group(3)}"
        
        # Extract email
        email_pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        email_match = re.search(email_pattern, user_input)
        if email_match:
            state.patient_info["email"] = email_match.group(1)

class PatientLookupAgent:
    """Agent responsible for patient lookup and EMR integration"""
    
    def __init__(self, db: MedicalDatabase, llm):
        self.db = db
        self.llm = llm
    
    def lookup_patient(self, state: AppointmentState) -> Dict[str, Any]:
        """Look up patient in EMR system"""
        
        patient_info = state.patient_info
        
        # Search for patient in database
        patient = self.db.find_patient(
            patient_info.get("first_name", ""),
            patient_info.get("last_name", ""),
            patient_info.get("date_of_birth")
        )
        
        if patient:
            # Update state with found patient info
            state.patient_info.update(patient)
            state.patient_info["is_new_patient"] = False
            
            message = f"Welcome back, {patient['first_name']}! I found your records. You're a returning patient."
            
            return {
                "next_step": "scheduling",
                "message": message,
                "patient_found": True,
                "patient_info": state.patient_info
            }
        else:
            # New patient
            state.patient_info["is_new_patient"] = True
            message = f"Hello {patient_info.get('first_name', 'there')}! I don't see you in our system, so you'll be a new patient. Let me help you schedule an appointment."
            
            return {
                "next_step": "scheduling",
                "message": message,
                "patient_found": False,
                "patient_info": state.patient_info
            }

class SchedulingAgent:
    """Agent responsible for smart scheduling and calendar management"""
    
    def __init__(self, db: MedicalDatabase, llm):
        self.db = db
        self.llm = llm
    
    def schedule_appointment(self, state: AppointmentState, user_input: str) -> Dict[str, Any]:
        """Handle appointment scheduling"""
        
        state.conversation_history.append({"role": "user", "content": user_input})
        
        # Determine appointment duration based on patient type
        is_new_patient = state.patient_info.get("is_new_patient", True)
        duration = NEW_PATIENT_DURATION if is_new_patient else RETURNING_PATIENT_DURATION
        
        # Get available slots
        preferred_doctor = state.patient_info.get("preferred_doctor")
        available_slots = self.db.get_available_slots(doctor_name=preferred_doctor)
        
        if not available_slots:
            return {
                "next_step": "scheduling",
                "message": "I'm sorry, but there are no available appointments at the moment. Please try again later or contact our office directly.",
                "appointment_details": state.appointment_details
            }
        
        # Present available options
        slots_text = "Here are the available appointment slots:\n"
        for i, slot in enumerate(available_slots[:5]):  # Show first 5 options
            slots_text += f"{i+1}. {slot['date']} at {slot['start_time']} with {slot['doctor_name']} ({slot['specialty']})\n"
        
        message = f"Great! I can schedule you for a {duration}-minute appointment. {slots_text}\nPlease let me know which option you prefer, or if you'd like to see more options."
        
        state.conversation_history.append({"role": "assistant", "content": message})
        
        return {
            "next_step": "scheduling",
            "message": message,
            "available_slots": available_slots[:5],
            "appointment_details": state.appointment_details
        }
    
    def confirm_appointment(self, state: AppointmentState, user_input: str) -> Dict[str, Any]:
        """Confirm appointment selection"""
        
        state.conversation_history.append({"role": "user", "content": user_input})
        
        # Extract selection from user input
        selection_match = re.search(r"(\d+)", user_input)
        if not selection_match:
            return {
                "next_step": "scheduling",
                "message": "I didn't catch that. Please select a number from the available options.",
                "appointment_details": state.appointment_details
            }
        
        selection = int(selection_match.group(1)) - 1
        available_slots = state.appointment_details.get("available_slots", [])
        
        if 0 <= selection < len(available_slots):
            selected_slot = available_slots[selection]
            
            # Book the appointment
            appointment_id = self.db.book_appointment(
                patient_id=state.patient_info["patient_id"],
                doctor_name=selected_slot["doctor_name"],
                appointment_date=selected_slot["date"],
                start_time=selected_slot["start_time"],
                duration=NEW_PATIENT_DURATION if state.patient_info.get("is_new_patient") else RETURNING_PATIENT_DURATION,
                reason="Routine appointment"
            )
            
            state.appointment_details = {
                "appointment_id": appointment_id,
                "doctor_name": selected_slot["doctor_name"],
                "date": selected_slot["date"],
                "start_time": selected_slot["start_time"],
                "duration": NEW_PATIENT_DURATION if state.patient_info.get("is_new_patient") else RETURNING_PATIENT_DURATION
            }
            
            message = f"Perfect! I've scheduled your appointment for {selected_slot['date']} at {selected_slot['start_time']} with {selected_slot['doctor_name']}. Your appointment ID is {appointment_id}."
            
            state.conversation_history.append({"role": "assistant", "content": message})
            
            return {
                "next_step": "insurance_collection",
                "message": message,
                "appointment_details": state.appointment_details
            }
        else:
            return {
                "next_step": "scheduling",
                "message": "That's not a valid selection. Please choose from the available options.",
                "appointment_details": state.appointment_details
            }

class InsuranceAgent:
    """Agent responsible for insurance collection and verification"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def collect_insurance_info(self, state: AppointmentState, user_input: str) -> Dict[str, Any]:
        """Collect insurance information"""
        
        state.conversation_history.append({"role": "user", "content": user_input})
        
        # Check if we already have insurance info
        if "insurance_carrier" in state.patient_info and state.patient_info["insurance_carrier"]:
            message = "I see you already have insurance information on file. Is this information still current, or would you like to update it?"
            state.conversation_history.append({"role": "assistant", "content": message})
            
            return {
                "next_step": "insurance_collection",
                "message": message,
                "insurance_info": state.patient_info
            }
        
        # Extract insurance information
        self._extract_insurance_info(user_input, state)
        
        # Check if we have all required insurance info
        required_insurance = ["insurance_carrier", "member_id"]
        missing_insurance = [field for field in required_insurance if field not in state.insurance_info]
        
        if missing_insurance:
            message = f"I need a bit more information about your insurance. Please provide your {', '.join(missing_insurance)}."
        else:
            message = "Thank you for the insurance information. Let me confirm your appointment details."
        
        state.conversation_history.append({"role": "assistant", "content": message})
        
        return {
            "next_step": "confirmation" if not missing_insurance else "insurance_collection",
            "message": message,
            "insurance_info": state.insurance_info
        }
    
    def _extract_insurance_info(self, user_input: str, state: AppointmentState):
        """Extract insurance information from user input"""
        
        # Common insurance carriers
        carriers = ["Blue Cross", "Aetna", "Cigna", "UnitedHealth", "Humana", "Kaiser", "Anthem"]
        
        for carrier in carriers:
            if carrier.lower() in user_input.lower():
                state.insurance_info["insurance_carrier"] = carrier
                break
        
        # Extract member ID
        member_id_pattern = r"member\s*id[:\s]*([A-Z0-9]+)"
        member_match = re.search(member_id_pattern, user_input, re.IGNORECASE)
        if member_match:
            state.insurance_info["member_id"] = member_match.group(1)

class ConfirmationAgent:
    """Agent responsible for appointment confirmation and final steps"""
    
    def __init__(self, db: MedicalDatabase, llm):
        self.db = db
        self.llm = llm
    
    def confirm_appointment(self, state: AppointmentState) -> Dict[str, Any]:
        """Confirm appointment and send forms"""
        
        appointment_details = state.appointment_details
        patient_info = state.patient_info
        
        # Generate confirmation message
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
        
        # Send intake forms
        form_type = "new_patient_form" if patient_info.get("is_new_patient") else "returning_patient_form"
        self.db.send_form(appointment_details["appointment_id"], form_type)
        
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
        
        state.completed = True
        state.conversation_history.append({"role": "assistant", "content": message})
        
        return {
            "next_step": "completed",
            "message": message,
            "appointment_details": appointment_details,
            "completed": True
        }

class MedicalAppointmentAgent:
    """Main orchestrator agent using LangGraph"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
        self.db = MedicalDatabase()
        
        # Initialize sub-agents
        self.greeting_agent = PatientGreetingAgent(self.llm)
        self.lookup_agent = PatientLookupAgent(self.db, self.llm)
        self.scheduling_agent = SchedulingAgent(self.db, self.llm)
        self.insurance_agent = InsuranceAgent(self.llm)
        self.confirmation_agent = ConfirmationAgent(self.db, self.llm)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AppointmentState)
        
        # Add nodes
        workflow.add_node("greeting", self._greeting_node)
        workflow.add_node("patient_lookup", self._lookup_node)
        workflow.add_node("scheduling", self._scheduling_node)
        workflow.add_node("insurance_collection", self._insurance_node)
        workflow.add_node("confirmation", self._confirmation_node)
        
        # Add edges
        workflow.add_edge("greeting", "patient_lookup")
        workflow.add_edge("patient_lookup", "scheduling")
        workflow.add_edge("scheduling", "insurance_collection")
        workflow.add_edge("insurance_collection", "confirmation")
        workflow.add_edge("confirmation", END)
        
        # Set entry point
        workflow.set_entry_point("greeting")
        
        return workflow.compile()
    
    def _greeting_node(self, state: AppointmentState, user_input: str = ""):
        """Greeting node handler"""
        return self.greeting_agent.greet_and_collect_info(state, user_input)
    
    def _lookup_node(self, state: AppointmentState):
        """Patient lookup node handler"""
        return self.lookup_agent.lookup_patient(state)
    
    def _scheduling_node(self, state: AppointmentState, user_input: str = ""):
        """Scheduling node handler"""
        if not state.appointment_details:
            return self.scheduling_agent.schedule_appointment(state, user_input)
        else:
            return self.scheduling_agent.confirm_appointment(state, user_input)
    
    def _insurance_node(self, state: AppointmentState, user_input: str = ""):
        """Insurance collection node handler"""
        return self.insurance_agent.collect_insurance_info(state, user_input)
    
    def _confirmation_node(self, state: AppointmentState):
        """Confirmation node handler"""
        return self.confirmation_agent.confirm_appointment(state)
    
    def process_message(self, user_input: str, state: AppointmentState = None) -> Dict[str, Any]:
        """Process user message through the workflow"""
        
        if state is None:
            state = AppointmentState()
        
        # Determine current step and route accordingly
        if state.current_step == "greeting":
            result = self._greeting_node(state, user_input)
        elif state.current_step == "patient_lookup":
            result = self._lookup_node(state)
        elif state.current_step == "scheduling":
            result = self._scheduling_node(state, user_input)
        elif state.current_step == "insurance_collection":
            result = self._insurance_node(state, user_input)
        elif state.current_step == "confirmation":
            result = self._confirmation_node(state)
        else:
            result = {"message": "I'm not sure how to help with that. Let me start over.", "next_step": "greeting"}
        
        # Update state
        state.current_step = result.get("next_step", state.current_step)
        
        return {
            "message": result.get("message", ""),
            "state": state,
            "completed": result.get("completed", False)
        }
