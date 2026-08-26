# Associate Onboarding Process

A production-style enterprise HR internal web application built with Python 3.11+, Streamlit, SQLite, SQLAlchemy ORM, and Plotly.

## Overview
The **Associate Onboar
ding Process** application enables HR and People Operations teams to manage the end-to-end onboarding lifecycle of new associates—from pre-onboarding checks to post-onboarding 90-day evaluations.

## Key Features
- **Onboarding Selection Screen**: Choice between starting a **NEW JOINER** onboarding or managing **EXISTING ASSOCIATES**.
- **Multi-Step Form with Validation**: Collect associate details with real-time email, phone, and date validation.
- **Conditional Work Mode Engine**: Automatically shows or hides asset shipping address and online-only tasks for Online vs Offline joiners.
- **3 Primary Onboarding Stages**:
  1. **Pre-Onboarding**: TA info, joiner connection, IT/Admin tickets, stakeholder notifications, schedule preparation.
  2. **Onboarding Day**: Mandatory BGV/bank/ISMS forms, NDA/appointment letters, HR induction walk-through, Viva Engage joiner announcement.
  3. **Post-Onboarding Activities**: ID card creation, HRMS document verification, 1-week, 30-day, 60-day, and 90-day feedback tracking with dynamic due dates.
- **Dynamic Progress Engine**: Computes stage and overall progress percentage strictly from applicable database task records.
- **Document Storage & Approval**: Secure upload handling (`uploads/{associate_id}/`) with status management (`Received`, `Approved`, `Rejected`).
- **Task Inventory**: Searchable and filterable task list by associate, stage, priority, and due date.
- **Enterprise Reports & Dashboards**: Visual analytics powered by Plotly for department distribution, stage completion, and overdue alerts.
- **Audit Activity Log**: Tracks all associate actions, document uploads, and task completions with timestamps.

## Project Structure
```
HR- On Boarding/
├── app.py                      # Main Streamlit application entrypoint & router
├── config.py                   # Application configuration & paths
├── database.py                 # SQLite ORM initialization & seeding mechanism
├── models.py                   # SQLAlchemy database models
├── requirements.txt            # Python dependencies
├── README.md                   # Setup and usage guide
├── workflow.md                 # Technical workflow specification
├── decesion.md                 # Architectural decision log
├── components/                 # Reusable Streamlit UI components
│   ├── sidebar.py
│   ├── header.py
│   ├── cards.py
│   ├── status_badge.py
│   ├── progress.py
│   ├── checklist.py
│   ├── employee_profile.py
│   ├── tables.py
│   └── forms.py
├── pages/                      # Page view implementations
│   ├── onboarding_selection.py
│   ├── new_onboarding.py
│   ├── onboarding_dashboard.py
│   ├── pre_onboarding.py
│   ├── onboarding_day.py
│   ├── post_onboarding.py
│   ├── existing_associates.py
│   ├── associate_details.py
│   ├── documents.py
│   ├── tasks.py
│   ├── dashboard.py
│   ├── reports.py
│   └── settings.py
├── services/                   # Business logic & repository services
│   ├── associate_service.py
│   ├── onboarding_service.py
│   ├── task_service.py
│   ├── progress_service.py
│   ├── document_service.py
│   ├── report_service.py
│   └── activity_service.py
├── utils/                      # Helper utilities
│   ├── constants.py
│   ├── validation.py
│   ├── formatting.py
│   └── file_utils.py
├── data/                       # SQLite database directory (onboarding.db)
├── uploads/                    # Associate uploaded document storage
└── tests/                      # Unit test suite
```

## Installation & Setup

1. **Clone/Navigate to directory**:
   ```bash
   cd "HR- On Boarding"
   ```

2. **Create & activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
```bash
streamlit run app.py
```

## Demo Data
Upon first startup, the database is automatically seeded with 5 realistic associate records across Engineering, HR, Data, AI, and Finance departments, featuring both Online and Offline work modes and varying completion stages.

## Running Tests
```bash
python -m unittest discover -s tests
```
# OnBoarding-Project
