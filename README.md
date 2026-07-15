# Gamage Recruiters - Executive Insights Dashboard

Enterprise-grade recruitment analytics platform with real-time performance tracking and automated reporting.

## 🏗️ Architecture|
gamage-recruiters-dashboard/
├── app.py # Main Streamlit UI
├── config/
│ └── settings.py # Global configuration
├── core/
│ ├── database.py # Data layer with encryption
│ └── analytics.py # Analytics engine
├── automation/
│ └── report_worker.py # Automated reporting daemon
├── reports/
│ └── generated/ # Auto-generated reports
├── Dockerfile # Container configuration
├── requirements.txt # Python dependencies
└── README.md # Documentation



## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py

# Run automation worker
python -m automation.report_worker


# Build image
docker build -t gamage-recruiters-dashboard .

# Run container
docker run -p 8501:8501 gamage-recruiters-dashboard

# Access dashboard
open http://localhost:8501

📊 Features
Executive KPIs
Total Placements & Revenue Tracking
Time-to-Hire Efficiency Metrics
Active Pipeline Management
Target Achievement Monitoring
Advanced Analytics
Multi-dimensional drill-down filtering
Client & Department performance analysis
Trend analysis with forecasting
Pipeline health scoring
Automation
Weekly automated report generation
PDF synthesis with executive summaries
Email distribution to stakeholders
Historical data archival
🔧 Configuration
Edit config/settings.py to customize:

KPI targets
Revenue parameters
UI theme colors
Email/SMTP settings
Report schedules
📈 Data Model
Pipeline States
Placed: Successfully hired candidates (revenue-generating)
Interviewing: Active interview process
Screening: Initial evaluation phase
Rejected: Not proceeding
Key Metrics
Revenue in LKR (Sri Lankan Rupees)
Time-to-hire in days
Conversion rates by stage
Pipeline velocity
🔐 Security
Field-level encryption simulation
Multi-tenant data isolation
Secure credential management
Audit logging for automation
📧 Automation Schedule
Weekly reports generated every Monday:

Executive summary PDF
Detailed JSON analytics
Raw CSV data export
Email distribution to leadership
🛠️ Technology Stack
Frontend: Streamlit
Visualization: Plotly Express/Graph Objects
Data Processing: Pandas, NumPy
Deployment: Docker
Automation: Python background workers
📞 Support
For issues or questions:

Email: virajrajaka12@gmail.com
Internal: IT Support PortalInit part 1
Init part 2
Init part 3
Init part 4
Init part 5
Init part 6
Init part 7
Init part 8
Init part 9
Init part 10
