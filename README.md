# 🏥 Medical Appointment Scheduling AI Agent

A comprehensive AI-powered medical appointment scheduling system built with LangGraph and LangChain that automates patient booking, reduces no-shows, and streamlines clinic operations.

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Project Overview

This project addresses the critical business problem in healthcare where medical practices lose 20-50% revenue due to no-shows, missed insurance collection, and scheduling inefficiencies. The AI agent provides an intelligent solution to these operational pain points.

### Business Problem
- **Revenue Loss**: 20-50% revenue loss due to no-shows
- **Scheduling Inefficiencies**: Manual appointment management
- **Insurance Collection**: Missed insurance verification
- **Patient Experience**: Poor booking experience

### Solution
- **AI-Powered Booking**: Intelligent conversation flow
- **Smart Scheduling**: 30min vs 60min appointment logic
- **Automated Reminders**: Email and SMS notifications
- **Data Management**: Excel export and reporting

## ✨ Key Features

### Core Features (MVP-1)
- **🤖 Patient Greeting & Data Collection**: Collects name, DOB, doctor preference with NLP validation
- **🔍 Patient Lookup**: Searches EMR system to detect new vs returning patients
- **📅 Smart Scheduling**: 60min slots for new patients, 30min for returning patients
- **📊 Calendar Integration**: Shows available slots with real-time availability checking
- **💳 Insurance Collection**: Captures carrier, member ID, and group information
- **✅ Appointment Confirmation**: Exports to Excel and sends confirmations
- **📄 Form Distribution**: Emails patient intake forms after confirmation
- **🔔 Reminder System**: 3 automated reminders with email and SMS notifications

### Advanced Features
- **🏗️ Multi-Agent Architecture**: LangGraph-based workflow with specialized agents
- **📈 Real-time Analytics**: Appointment trends and doctor performance metrics
- **📊 Excel Export**: Comprehensive reporting and data export capabilities
- **🛡️ Error Handling**: Robust error handling and edge case management
- **🌐 Web Interface**: Modern Streamlit-based user interface
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

### Technical Stack
- **Framework**: LangGraph + LangChain
- **LLM**: OpenAI GPT-3.5-turbo (optional for demo)
- **Database**: SQLite with pandas integration
- **Frontend**: Streamlit
- **Communication**: SMTP (Email) + Twilio (SMS)
- **Data Export**: Excel with openpyxl
- **Analytics**: Plotly for charts

### Agent Architecture
```
MedicalAppointmentAgent (Orchestrator)
├── PatientGreetingAgent (Data Collection)
├── PatientLookupAgent (EMR Integration)
├── SchedulingAgent (Calendar Management)
├── InsuranceAgent (Insurance Collection)
└── ConfirmationAgent (Final Steps)
```

### Data Flow
1. **Patient Input** → Greeting Agent (NLP Processing)
2. **Data Collection** → Lookup Agent (EMR Search)
3. **Patient Classification** → Scheduling Agent (Smart Scheduling)
4. **Insurance Collection** → Insurance Agent (Data Structuring)
5. **Confirmation** → Confirmation Agent (Forms & Reminders)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- OpenAI API Key (optional for demo)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd medical-appointment-ai
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Demo Setup
```bash
python setup_demo.py
```

### 5. Start the Application
```bash
python main.py --web
```

The application will be available at `http://localhost:8501`

## 📦 Installation

### Method 1: Automated Setup (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd medical-appointment-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Run automated setup
python setup_demo.py

# Start application
python main.py --web
```

### Method 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Generate sample data
python data_generator.py

# Initialize database
python database.py

# Start application
python main.py --web
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# OpenAI API Key (Optional for demo)
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Database Configuration
DATABASE_URL=sqlite:///medical_appointments.db
```

### Business Logic Configuration
Edit `config.py` to customize:

```python
NEW_PATIENT_DURATION = 60  # minutes
RETURNING_PATIENT_DURATION = 30  # minutes
APPOINTMENT_BUFFER = 15  # minutes between appointments
REMINDER_1_HOURS = 24  # 24 hours before
REMINDER_2_HOURS = 2   # 2 hours before
REMINDER_3_HOURS = 1   # 1 hour before
```

## 🎮 Usage

### Web Interface
1. **Start the app**: `python main.py --web`
2. **Open browser**: Navigate to `http://localhost:8501`
3. **Initialize system**: Click "Initialize System" in sidebar
4. **Start chatting**: Use the chat interface to book appointments

### CLI Demo
```bash
python main.py --demo
```

### Command Line Options
```bash
python main.py --help

Options:
  --setup     Set up the environment
  --demo      Run CLI demo
  --web       Run web interface (default)
  --data      Generate sample data only
  --init-db   Initialize database only
```

## 📊 Features in Detail

### 1. Patient Registration
- **Natural Language Processing**: Understands various ways to provide information
- **Data Validation**: Ensures required fields are collected
- **Patient Classification**: Automatically detects new vs returning patients

### 2. Smart Scheduling
- **Duration Logic**: 60min for new patients, 30min for returning
- **Availability Checking**: Real-time slot availability
- **Conflict Prevention**: Prevents double-booking

### 3. Insurance Collection
- **Carrier Recognition**: Identifies common insurance providers
- **Member ID Extraction**: Captures insurance details
- **Data Structuring**: Organizes insurance information

### 4. Appointment Management
- **Real-time Updates**: Live appointment tracking
- **Excel Export**: Comprehensive reporting
- **Database Integration**: Persistent data storage

### 5. Communication
- **Email Notifications**: Appointment confirmations and reminders
- **SMS Alerts**: Mobile notifications
- **Form Distribution**: Automated intake form sending

## 📈 Analytics & Reporting

### Available Reports
- **Daily Reports**: Appointment summary for specific dates
- **Weekly Reports**: 7-day appointment trends and analysis
- **Monthly Reports**: Comprehensive monthly statistics
- **Doctor Performance**: Individual doctor appointment metrics
- **Patient Reports**: Individual patient appointment history

### Export Formats
- **Excel (.xlsx)**: Multiple sheets with detailed data
- **CSV**: For data analysis
- **PDF**: Future enhancement

## 🛠️ API Documentation

### Core Classes

#### `SimpleAppointmentAgent`
Main agent class for appointment booking.

```python
agent = SimpleAppointmentAgent()
result = agent.process_message("Hi, I'd like to book an appointment")
```

#### `MedicalDatabase`
Database management for appointments and patients.

```python
db = MedicalDatabase()
appointments = db.get_appointments_for_export()
```

#### `ExcelExporter`
Export functionality for reports.

```python
exporter = ExcelExporter(db)
filepath = exporter.export_appointments()
```

### Key Methods

#### Patient Management
- `find_patient(first_name, last_name, dob)`: Find patient in database
- `book_appointment(patient_id, doctor, date, time, duration)`: Book appointment
- `get_available_slots(doctor, date)`: Get available time slots

#### Data Export
- `export_appointments()`: Export all appointments
- `export_daily_appointments(date)`: Export daily report
- `export_weekly_report(start_date)`: Export weekly report

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install requirements
pip install -r requirements.txt
```

#### 2. Database Connection Issues
```bash
# Solution: Reinitialize database
python main.py --init-db
```

#### 3. API Key Issues
```bash
# Solution: Update .env file
nano .env
# Add your API keys
```

#### 4. Port Conflicts
```bash
# Solution: Kill existing processes
lsof -ti:8501 | xargs kill -9
```

### Debug Mode
Enable debug output by adding to your code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files
Check logs in the `logs/` directory for detailed error information.

## 📁 Project Structure

```
medical-appointment-ai/
├── agents.py              # LangGraph agent implementations
├── app.py                 # Streamlit web interface
├── communication.py       # Email and SMS services
├── config.py              # Configuration management
├── database.py            # Database operations
├── data_generator.py      # Synthetic data generation
├── excel_export.py        # Excel export functionality
├── main.py                # Main entry point
├── simple_agent.py        # Simplified agent (demo)
├── setup_demo.py          # Demo setup script
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── data/                  # Sample data files
│   ├── patients.csv       # Patient database
│   ├── doctor_schedules.xlsx
│   └── intake_forms.json
├── exports/               # Generated reports
├── templates/             # Form templates
└── logs/                  # Application logs
```

## 🧪 Testing

### Test Data
The system includes 50 synthetic patients with realistic data:
- Patient demographics and contact information
- Insurance information
- Medical history
- Doctor preferences

### Test Scenarios
- New patient registration
- Returning patient lookup
- Appointment scheduling
- Insurance collection
- Form distribution
- Reminder system

### Running Tests
```bash
# Run demo to test functionality
python demo.py

# Test specific components
python -c "from simple_agent import SimpleAppointmentAgent; print('Agent test passed')"
```

## 🔒 Security & Privacy

### Data Protection
- Patient data stored in encrypted SQLite database
- API keys stored in environment variables
- No hardcoded credentials in source code
- Secure email and SMS transmission

### Compliance
- HIPAA-compliant data handling practices
- Secure patient information management
- Audit trail for all appointments
- Data retention policies

## 🚀 Deployment

### Local Development
```bash
python main.py --web
```

### Production Deployment
1. Set up production database (PostgreSQL)
2. Configure environment variables
3. Set up reverse proxy (Nginx)
4. Use process manager (PM2, systemd)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 🔮 Future Enhancements

### Planned Features
- **Voice Integration**: Voice-based appointment booking
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Machine learning insights
- **Integration APIs**: EMR system integration
- **Multi-language Support**: Internationalization
- **Telemedicine Integration**: Virtual appointment support

### Scalability Improvements
- **Database Migration**: PostgreSQL for production
- **Microservices**: Containerized deployment
- **Load Balancing**: High availability setup
- **Caching**: Redis for performance optimization

## 🤝 Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/medical-appointment-ai.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Write unit tests for new features

## 📞 Support

### Getting Help
- **GitHub Issues**: [Repository Issues](https://github.com/your-repo/issues)
- **Documentation**: Check this README
- **Email**: suryaashokan57@gmail.com

### FAQ

**Q: Do I need API keys to run the demo?**
A: No, the demo works without API keys. Email/SMS features require API keys.

**Q: Can I use a different database?**
A: Yes, modify `database.py` to use PostgreSQL, MySQL, etc.

**Q: How do I customize the appointment duration?**
A: Edit `config.py` to change `NEW_PATIENT_DURATION` and `RETURNING_PATIENT_DURATION`.

**Q: Can I add more doctors?**
A: Yes, modify `data_generator.py` to add more doctors to the schedule.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For the AI agent framework
- **Streamlit**: For the web interface
- **OpenAI**: For the language model
- **Healthcare Community**: For domain expertise

---

*Last updated: January 2025*
