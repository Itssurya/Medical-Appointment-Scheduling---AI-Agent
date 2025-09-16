#!/usr/bin/env python3
"""
Demo setup script for Medical Appointment Scheduling AI Agent
This version works without API keys for demonstration purposes
"""

import os
import sys
import subprocess
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
    """Create .env file with demo values"""
    if not os.path.exists(".env"):
        env_content = """# OpenAI API Key (Optional for demo)
OPENAI_API_KEY=demo_key

# Email Configuration (Optional for demo)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=demo@example.com
EMAIL_PASSWORD=demo_password

# Twilio Configuration (Optional for demo)
TWILIO_ACCOUNT_SID=demo_sid
TWILIO_AUTH_TOKEN=demo_token
TWILIO_PHONE_NUMBER=+1234567890

# Database Configuration
DATABASE_URL=sqlite:///medical_appointments.db
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✓ Created .env file with demo values")
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

def test_system():
    """Test the system"""
    print("Testing system...")
    try:
        from simple_agent import SimpleAppointmentAgent
        from database import MedicalDatabase
        
        # Test agent
        agent = SimpleAppointmentAgent()
        print("✓ Agent initialized successfully")
        
        # Test database
        db = MedicalDatabase()
        print("✓ Database connected successfully")
        
        return True
    except Exception as e:
        print(f"Error testing system: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Medical Appointment Scheduling AI Agent - Demo Setup")
    print("=" * 60)
    print()
    
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
    
    # Test system
    if not test_system():
        return False
    
    print("=" * 60)
    print("Demo setup completed successfully!")
    print("=" * 60)
    print()
    print("The system is ready to run without API keys!")
    print()
    print("To start the application:")
    print("  python main.py --web")
    print()
    print("Features available in demo mode:")
    print("  ✅ Patient data collection")
    print("  ✅ Appointment scheduling")
    print("  ✅ Database operations")
    print("  ✅ Excel export")
    print("  ✅ Form generation")
    print("  ⚠️  Email/SMS (requires API keys)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

