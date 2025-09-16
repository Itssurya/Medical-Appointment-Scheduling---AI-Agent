import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go

# Import our modules
from simple_agent import SimpleAppointmentAgent
from database import initialize_database
from excel_export import ExcelExporter, ReportGenerator
from communication import EmailService, SMSService, FormGenerator
from data_generator import create_sample_data

# Page configuration
st.set_page_config(
    page_title="Medical Appointment Scheduling AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #F3E5F5;
        margin-right: 2rem;
    }
    .appointment-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .success-message {
        color: #4CAF50;
        font-weight: bold;
    }
    .error-message {
        color: #F44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'appointment_state' not in st.session_state:
    st.session_state.appointment_state = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'appointments' not in st.session_state:
    st.session_state.appointments = []
if 'db' not in st.session_state:
    st.session_state.db = None
if 'email_service' not in st.session_state:
    st.session_state.email_service = None
if 'sms_service' not in st.session_state:
    st.session_state.sms_service = None
if 'form_generator' not in st.session_state:
    st.session_state.form_generator = None

def initialize_system():
    """Initialize the medical appointment system"""
    try:
        # Create sample data if it doesn't exist
        if not os.path.exists("data/patients.csv"):
            st.info("Creating sample data...")
            create_sample_data()
        
        # Initialize database
        db = initialize_database()
        
        # Initialize simplified agent
        agent = SimpleAppointmentAgent()
        
        # Initialize services
        email_service = EmailService()
        sms_service = SMSService()
        form_generator = FormGenerator()
        
        return agent, db, email_service, sms_service, form_generator
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return None, None, None, None, None

def display_chat_message(message: str, is_user: bool = False):
    """Display a chat message"""
    if is_user:
        st.markdown(f'<div class="chat-message user-message">👤 {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message">🤖 {message}</div>', unsafe_allow_html=True)

def display_appointment_card(appointment: Dict):
    """Display appointment information in a card"""
    st.markdown(f"""
    <div class="appointment-card">
        <h4>Appointment {appointment.get('appointment_id', 'N/A')}</h4>
        <p><strong>Patient:</strong> {appointment.get('first_name', '')} {appointment.get('last_name', '')}</p>
        <p><strong>Doctor:</strong> {appointment.get('doctor_name', 'N/A')}</p>
        <p><strong>Date:</strong> {appointment.get('appointment_date', 'N/A')}</p>
        <p><strong>Time:</strong> {appointment.get('start_time', 'N/A')} - {appointment.get('end_time', 'N/A')}</p>
        <p><strong>Duration:</strong> {appointment.get('duration', 'N/A')} minutes</p>
        <p><strong>Status:</strong> {appointment.get('status', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Medical Appointment Scheduling AI Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("System Controls")
        
        if st.button("Initialize System", type="primary"):
            with st.spinner("Initializing system..."):
                agent, db, email_service, sms_service, form_generator = initialize_system()
                if agent:
                    st.session_state.agent = agent
                    st.session_state.db = db
                    st.session_state.email_service = email_service
                    st.session_state.sms_service = sms_service
                    st.session_state.form_generator = form_generator
                    st.success("System initialized successfully!")
                else:
                    st.error("Failed to initialize system")
        
        st.divider()
        
        if st.button("Reset Conversation"):
            st.session_state.conversation_history = []
            st.session_state.appointment_state = None
            st.rerun()
        
        st.divider()
        
        # System status
        st.header("System Status")
        if st.session_state.agent:
            st.success("✅ Agent Ready")
        else:
            st.error("❌ Agent Not Initialized")
        
        if st.session_state.db:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Not Connected")
    
    # Main content
    if not st.session_state.agent:
        st.warning("Please initialize the system first using the sidebar.")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🤖 Chat Interface", 
        "📅 Appointments", 
        "📊 Reports", 
        "📧 Communication", 
        "⚙️ Settings"
    ])
    
    with tab1:
        st.header("Chat with the AI Agent")
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            for message in st.session_state.conversation_history:
                display_chat_message(message["content"], message["role"] == "user")
        
        # User input
        user_input = st.text_input("Type your message here:", key="user_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send", type="primary"):
                if user_input:
                    # Process message
                    result = st.session_state.agent.process_message(user_input)
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "role": "user", 
                        "content": user_input
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant", 
                        "content": result["message"]
                    })
                    
                    # If appointment is completed, add to appointments list
                    if result.get("completed") and st.session_state.agent.appointment_details:
                        appointment_data = {
                            "appointment_id": st.session_state.agent.appointment_details["appointment_id"],
                            "first_name": st.session_state.agent.patient_info.get("first_name", ""),
                            "last_name": st.session_state.agent.patient_info.get("last_name", ""),
                            "doctor_name": st.session_state.agent.appointment_details["doctor_name"],
                            "appointment_date": st.session_state.agent.appointment_details["date"],
                            "start_time": st.session_state.agent.appointment_details["start_time"],
                            "end_time": st.session_state.agent.appointment_details.get("end_time", ""),
                            "duration": st.session_state.agent.appointment_details["duration"],
                            "status": "scheduled"
                        }
                        st.session_state.appointments.append(appointment_data)
                        st.success("Appointment added to your list!")
                    
                    # Also add appointment when it's booked (not just when completed)
                    elif st.session_state.agent.appointment_details and "appointment_id" in st.session_state.agent.appointment_details:
                        # Check if this appointment is already in the list
                        appointment_id = st.session_state.agent.appointment_details["appointment_id"]
                        existing_appointments = [apt for apt in st.session_state.appointments if apt.get("appointment_id") == appointment_id]
                        
                        if not existing_appointments:
                            appointment_data = {
                                "appointment_id": st.session_state.agent.appointment_details["appointment_id"],
                                "first_name": st.session_state.agent.patient_info.get("first_name", ""),
                                "last_name": st.session_state.agent.patient_info.get("last_name", ""),
                                "doctor_name": st.session_state.agent.appointment_details["doctor_name"],
                                "appointment_date": st.session_state.agent.appointment_details["date"],
                                "start_time": st.session_state.agent.appointment_details["start_time"],
                                "end_time": st.session_state.agent.appointment_details.get("end_time", ""),
                                "duration": st.session_state.agent.appointment_details["duration"],
                                "status": "scheduled"
                            }
                            st.session_state.appointments.append(appointment_data)
                            st.success("Appointment added to your list!")
                    
                    st.rerun()
        
        with col2:
            if st.button("Clear Chat"):
                st.session_state.conversation_history = []
                if st.session_state.agent:
                    st.session_state.agent.reset()
                st.rerun()
    
    with tab2:
        st.header("Appointment Management")
        
        # Refresh button
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("Refresh Appointments"):
                st.rerun()
        with col2:
            if st.button("Load from Database"):
                if st.session_state.db:
                    try:
                        # Load appointments from database
                        db_appointments = st.session_state.db.get_appointments_for_export()
                        if not db_appointments.empty:
                            # Convert to session state format
                            for _, row in db_appointments.iterrows():
                                appointment_data = {
                                    "appointment_id": row["appointment_id"],
                                    "first_name": row["first_name"],
                                    "last_name": row["last_name"],
                                    "doctor_name": row["doctor_name"],
                                    "appointment_date": row["appointment_date"],
                                    "start_time": row["start_time"],
                                    "end_time": row["end_time"],
                                    "duration": row["duration"],
                                    "status": row["status"]
                                }
                                # Check if already exists
                                existing = [apt for apt in st.session_state.appointments if apt.get("appointment_id") == row["appointment_id"]]
                                if not existing:
                                    st.session_state.appointments.append(appointment_data)
                            st.success(f"Loaded {len(db_appointments)} appointments from database!")
                        else:
                            st.info("No appointments found in database.")
                    except Exception as e:
                        st.error(f"Error loading from database: {e}")
                else:
                    st.error("Database not available")
        
        # Display current appointments
        if st.session_state.appointments:
            st.subheader(f"Recent Appointments ({len(st.session_state.appointments)})")
            for appointment in st.session_state.appointments:
                display_appointment_card(appointment)
        else:
            st.info("No appointments scheduled yet.")
            st.info("💡 Tip: Book an appointment in the Chat Interface tab to see it here!")
        
        # Export appointments
        if st.button("Export Appointments to Excel"):
            if st.session_state.db:
                exporter = ExcelExporter(st.session_state.db)
                filepath = exporter.export_appointments()
                st.success(f"Appointments exported to {filepath}")
            else:
                st.error("Database not available")
        
        # View all appointments from database
        if st.button("View All Appointments"):
            if st.session_state.db:
                appointments_df = st.session_state.db.get_appointments_for_export()
                if not appointments_df.empty:
                    st.dataframe(appointments_df)
                    st.info(f"Found {len(appointments_df)} appointments in database")
                    st.info(f"Available dates: {', '.join(appointments_df['appointment_date'].unique())}")
                else:
                    st.info("No appointments found in database")
            else:
                st.error("Database not available")
        
        # Debug database
        if st.button("Debug Database"):
            if st.session_state.db:
                try:
                    # Get raw appointments from database
                    conn = st.session_state.db.db_path
                    import sqlite3
                    conn_sqlite = sqlite3.connect(conn)
                    cursor = conn_sqlite.cursor()
                    cursor.execute("SELECT * FROM appointments")
                    rows = cursor.fetchall()
                    conn_sqlite.close()
                    
                    if rows:
                        st.success(f"Found {len(rows)} appointments in raw database")
                        for row in rows:
                            st.write(f"ID: {row[0]}, Patient: {row[1]}, Doctor: {row[2]}, Date: {row[3]}")
                    else:
                        st.info("No appointments in raw database")
                except Exception as e:
                    st.error(f"Database error: {e}")
            else:
                st.error("Database not available")
    
    with tab3:
        st.header("Reports & Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Report")
            report_date = st.date_input("Select Date", value=datetime.now().date())
            if st.button("Generate Daily Report"):
                if st.session_state.db:
                    exporter = ExcelExporter(st.session_state.db)
                    filepath = exporter.export_daily_appointments(report_date.strftime("%Y-%m-%d"))
                    if filepath:
                        st.success(f"Daily report exported to {filepath}")
                    else:
                        st.info("No appointments found for selected date")
                else:
                    st.error("Database not available")
        
        with col2:
            st.subheader("Weekly Report")
            week_start = st.date_input("Select Week Start", value=datetime.now().date())
            if st.button("Generate Weekly Report"):
                if st.session_state.db:
                    generator = ReportGenerator(st.session_state.db)
                    filepath = generator.generate_weekly_report(week_start.strftime("%Y-%m-%d"))
                    st.success(f"Weekly report exported to {filepath}")
                else:
                    st.error("Database not available")
        
        # Analytics charts
        if st.session_state.db:
            st.subheader("Appointment Analytics")
            
            # Get appointments data
            appointments_df = st.session_state.db.get_appointments_for_export()
            
            if not appointments_df.empty:
                # Doctor distribution
                doctor_counts = appointments_df['doctor_name'].value_counts()
                fig1 = px.pie(values=doctor_counts.values, names=doctor_counts.index, 
                             title="Appointments by Doctor")
                st.plotly_chart(fig1, use_container_width=True)
                
                # Daily appointment trends
                appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date'])
                daily_counts = appointments_df.groupby(appointments_df['appointment_date'].dt.date).size()
                fig2 = px.line(x=daily_counts.index, y=daily_counts.values, 
                              title="Daily Appointment Trends")
                fig2.update_xaxes(title="Date")
                fig2.update_yaxes(title="Number of Appointments")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No appointment data available for analytics")
    
    with tab4:
        st.header("Communication Management")
        
        # Email settings
        st.subheader("Email Configuration")
        email_host = st.text_input("SMTP Host", value="smtp.gmail.com")
        email_port = st.number_input("SMTP Port", value=587)
        email_username = st.text_input("Email Username")
        email_password = st.text_input("Email Password", type="password")
        
        if st.button("Test Email Connection"):
            try:
                email_service = EmailService()
                st.success("Email service configured successfully!")
            except Exception as e:
                st.error(f"Email configuration failed: {str(e)}")
        
        # SMS settings
        st.subheader("SMS Configuration")
        twilio_sid = st.text_input("Twilio Account SID")
        twilio_token = st.text_input("Twilio Auth Token", type="password")
        twilio_phone = st.text_input("Twilio Phone Number")
        
        if st.button("Test SMS Connection"):
            try:
                sms_service = SMSService()
                st.success("SMS service configured successfully!")
            except Exception as e:
                st.error(f"SMS configuration failed: {str(e)}")
        
        # Send test messages
        st.subheader("Send Test Messages")
        test_email = st.text_input("Test Email Address")
        test_phone = st.text_input("Test Phone Number")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send Test Email"):
                if test_email and st.session_state.email_service:
                    success = st.session_state.email_service.send_appointment_confirmation(
                        test_email, 
                        {"patient_name": "Test Patient", "appointment_id": "TEST123", 
                         "doctor_name": "Dr. Test", "date": "2024-01-15", 
                         "start_time": "10:00", "duration": 30}
                    )
                    if success:
                        st.success("Test email sent successfully!")
                    else:
                        st.error("Failed to send test email")
        
        with col2:
            if st.button("Send Test SMS"):
                if test_phone and st.session_state.sms_service:
                    success = st.session_state.sms_service.send_appointment_confirmation(
                        test_phone,
                        {"appointment_id": "TEST123", "doctor_name": "Dr. Test", 
                         "date": "2024-01-15", "start_time": "10:00"}
                    )
                    if success:
                        st.success("Test SMS sent successfully!")
                    else:
                        st.error("Failed to send test SMS")
    
    with tab5:
        st.header("System Settings")
        
        # Database management
        st.subheader("Database Management")
        if st.button("Reinitialize Database"):
            with st.spinner("Reinitializing database..."):
                db = initialize_database()
                if db:
                    st.session_state.db = db
                    st.success("Database reinitialized successfully!")
                else:
                    st.error("Failed to reinitialize database")
        
        # Data management
        st.subheader("Data Management")
        if st.button("Regenerate Sample Data"):
            with st.spinner("Generating sample data..."):
                create_sample_data()
                st.success("Sample data regenerated successfully!")
        
        # System information
        st.subheader("System Information")
        st.info(f"""
        **Agent Status:** {'Ready' if st.session_state.agent else 'Not Initialized'}
        **Database Status:** {'Connected' if st.session_state.db else 'Not Connected'}
        **Email Service:** {'Available' if st.session_state.email_service else 'Not Available'}
        **SMS Service:** {'Available' if st.session_state.sms_service else 'Not Available'}
        **Total Appointments:** {len(st.session_state.appointments)}
        """)

if __name__ == "__main__":
    main()
