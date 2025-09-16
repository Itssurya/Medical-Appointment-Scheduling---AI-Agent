import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Email Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")

# Twilio Configuration (for SMS)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_twilio_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_twilio_auth_token")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "your_twilio_phone_number")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///medical_appointments.db")

# Business Logic Configuration
NEW_PATIENT_DURATION = 60  # minutes
RETURNING_PATIENT_DURATION = 30  # minutes
APPOINTMENT_BUFFER = 15  # minutes between appointments

# Reminder Configuration
REMINDER_1_HOURS = 24  # 24 hours before
REMINDER_2_HOURS = 2   # 2 hours before
REMINDER_3_HOURS = 1   # 1 hour before
