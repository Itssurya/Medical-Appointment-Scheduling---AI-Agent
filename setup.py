#!/usr/bin/env python3
"""
Setup script for Medical Appointment Scheduling AI Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["data", "exports", "templates", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists(".env"):
        env_content = """# OpenAI API Key
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
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")

def generate_sample_data():
    """Generate sample data"""
    print("Generating sample data...")
    try:
        from data_generator import create_sample_data
        create_sample_data()
        print("✓ Sample data generated successfully")
        return True
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return False

def initialize_database():
    """Initialize database"""
    print("Initializing database...")
    try:
        from database import initialize_database
        db = initialize_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print("Running basic tests...")
    try:
        # Test imports
        from agents import MedicalAppointmentAgent
        from database import MedicalDatabase
        from communication import EmailService, SMSService
        print("✓ All imports successful")
        
        # Test agent initialization
        agent = MedicalAppointmentAgent()
        print("✓ Agent initialization successful")
        
        return True
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Medical Appointment Scheduling AI Agent - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Generate sample data
    if not generate_sample_data():
        return False
    
    # Initialize database
    if not initialize_database():
        return False
    
    # Run tests
    if not run_tests():
        return False
    
    print("=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("Next steps:")
    print("1. Update the .env file with your API keys and credentials")
    print("2. Run the application:")
    print("   - Web interface: python main.py --web")
    print("   - CLI demo: python main.py --demo")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
