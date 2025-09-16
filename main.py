#!/usr/bin/env python3
"""
Medical Appointment Scheduling AI Agent
Main entry point for the application
"""

import os
import sys
import argparse
from datetime import datetime

def setup_environment():
    """Set up the environment and dependencies"""
    print("Setting up Medical Appointment Scheduling AI Agent...")
    
    # Create necessary directories
    directories = ["data", "exports", "templates", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Creating .env file from template...")
        with open(".env", "w") as f:
            f.write("""# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Twilio Configuration (for SMS)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Database Configuration
DATABASE_URL=sqlite:///medical_appointments.db
""")
        print("Please update the .env file with your actual API keys and credentials.")
    
    print("Environment setup complete!")

def generate_sample_data():
    """Generate sample data for testing"""
    print("Generating sample data...")
    
    try:
        from data_generator import create_sample_data
        create_sample_data()
        print("Sample data generated successfully!")
    except Exception as e:
        print(f"Error generating sample data: {str(e)}")
        return False
    
    return True

def initialize_database():
    """Initialize the database with sample data"""
    print("Initializing database...")
    
    try:
        from database import initialize_database
        db = initialize_database()
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    print("Starting Streamlit application...")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {str(e)}")
        return False
    except KeyboardInterrupt:
        print("Streamlit app stopped by user")
        return True

def run_cli_demo():
    """Run a command-line interface demo"""
    print("Starting CLI demo...")
    
    try:
        from agents import MedicalAppointmentAgent, AppointmentState
        
        # Initialize agent
        agent = MedicalAppointmentAgent()
        state = AppointmentState()
        
        print("\n" + "="*60)
        print("Medical Appointment Scheduling AI Agent - CLI Demo")
        print("="*60)
        print("Type 'quit' to exit the demo")
        print("="*60)
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process message
            result = agent.process_message(user_input, state)
            
            print(f"\nAgent: {result['message']}")
            
            # Update state
            state = result['state']
            
            # Check if appointment is completed
            if result.get('completed'):
                print("\n" + "="*60)
                print("APPOINTMENT BOOKED SUCCESSFULLY!")
                print("="*60)
                break
    
    except Exception as e:
        print(f"Error running CLI demo: {str(e)}")
        return False
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Medical Appointment Scheduling AI Agent")
    parser.add_argument("--setup", action="store_true", help="Set up the environment")
    parser.add_argument("--demo", action="store_true", help="Run CLI demo")
    parser.add_argument("--web", action="store_true", help="Run web interface")
    parser.add_argument("--data", action="store_true", help="Generate sample data only")
    parser.add_argument("--init-db", action="store_true", help="Initialize database only")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_environment()
        return
    
    if args.data:
        generate_sample_data()
        return
    
    if args.init_db:
        initialize_database()
        return
    
    if args.demo:
        run_cli_demo()
        return
    
    if args.web:
        run_streamlit_app()
        return
    
    # Default: run web interface
    print("Medical Appointment Scheduling AI Agent")
    print("=====================================")
    print("Available options:")
    print("  --setup     Set up the environment")
    print("  --demo      Run CLI demo")
    print("  --web       Run web interface (default)")
    print("  --data      Generate sample data only")
    print("  --init-db   Initialize database only")
    print()
    
    choice = input("Choose an option (1-5) or press Enter for web interface: ").strip()
    
    if choice == "1":
        setup_environment()
    elif choice == "2":
        run_cli_demo()
    elif choice == "3":
        run_streamlit_app()
    elif choice == "4":
        generate_sample_data()
    elif choice == "5":
        initialize_database()
    else:
        # Default to web interface
        run_streamlit_app()

if __name__ == "__main__":
    main()
