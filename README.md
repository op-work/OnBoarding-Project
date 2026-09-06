# Onboarding Operations System

A production-ready enterprise HR web application built with **Python 3.11+**, **Streamlit**, **Azure Database for PostgreSQL Flexible Server**, **SQLAlchemy 2.0 ORM**, and **Plotly**. Designed for deployment on **Azure Web App (Linux App Service)**.

---

## 📌 Executive Summary

The **Onboarding Operations System** streamlines candidate onboarding for HR and People Operations teams—guiding new joiners from pre-onboarding checks, Day 1 orientation, and post-onboarding 90-day evaluations to final probation confirmation.

---

## 🛠 Key Features

1. **Enterprise Authentication Guard**:
   - Secure login portal using JWT (JSON Web Token) credential validation.
   - Session state routing protection and default HR Admin seeding (`admin@company.com`).

2. **Dual Registration Channels**:
   - **Single Joiner Registration**: 7-field validated form capturing Aadhar name, DOJ, personal email, fresher status/LWD, designation, location, work mode, and shipping address.
   - **Bulk Employee Import**: Multi-format ingestion (`.xlsx`, `.xls`, `.csv`, `.json`) mapping up to 71 HR system columns with automatic duplicate checking and `UPSERT` profile updates.

3. **Dynamic 14-Milestone Progress Engine**:
   - Computes progress percentage dynamically from 14 verified database checklist items across 3 primary stages:
     - **Pre-Onboarding** (6 items): TA info, joiner connection, IT tickets, stakeholder notification, schedule prep & delivery.
     - **Onboarding Day** (4 items): Mandatory BGV/bank/ISMS forms, NDA/docs verification, HR induction, Viva Engage announcement.
     - **Post-Onboarding** (4 items): ID card request, HRMS document verification (`Approved` status), 1-week check-in, insurance/PF registration.

4. **Feedback & 90-Day Probation Tracker**:
   - Tracks 30-day, 60-day, and 90-day manager/associate feedback checkpoints.
   - Transitions associate probation status from `Under Review` to `Confirmed`.

5. **Analytics & Audit Logging**:
   - Real-time Plotly charts for department distribution, stage progress, work mode metrics, and overdue tasks.
   - Database-backed `ActivityLog` tracking system events, document uploads, and milestone updates with exact timestamps.

---

## 📂 Project Architecture & Workflow Documentation

Detailed technical architecture and operational workflow block diagrams are documented in the [`project_info/`](./project_info/) directory:

- 📐 [**Project Architecture Diagram (`project_info/architecture.md`)**](./project_info/architecture.md): Block diagram detailing Azure Web App container, Streamlit presentation layer, JWT security, business services, SQLAlchemy ORM, and Azure PostgreSQL Flexible Server with SSL.
- 🔄 [**End-to-End Workflow Diagram (`project_info/workflow.md`)**](./project_info/workflow.md): Complete block diagram tracing candidate journey from user authentication, candidate entry (single/bulk import), 3-stage milestone execution, probation sign-off, to analytics reporting.

---

## 📁 Repository Structure

```
HR- On Boarding/
├── app.py                      # Main Streamlit application entrypoint & router
├── config.py                   # Environment & Azure PostgreSQL configuration
├── database.py                 # Azure PostgreSQL session management & demo data seeder
├── models.py                   # SQLAlchemy ORM database models
├── requirements.txt            # Python production dependencies
├── .env.example                # Environment variable configuration template
├── README.md                   # Production setup & deployment documentation
├── project_info/               # Project architecture & workflow documentation
│   ├── architecture.md         # Architecture block diagram & technical specs
│   └── workflow.md             # End-to-end user workflow block diagrams
├── components/                 # Reusable Streamlit UI components
│   ├── sidebar.py              # Navigation sidebar with authenticated state
│   ├── header.py               # Page header component
│   ├── cards.py                # Metric & summary cards
│   ├── status_badge.py         # Custom HTML pill status badges
│   ├── progress.py             # Progress bars & stage metrics
│   ├── checklist.py            # Milestone interactive checklists
│   └── employee_profile.py     # Associate details view layout
├── views/                      # Application page views
│   ├── auth.py                 # Login portal view
│   ├── onboarding_selection.py # Onboarding Hub selection screen
│   ├── new_onboarding.py       # Single joiner registration form
│   ├── onboarding_dashboard.py # Active onboarding operational board
│   ├── pre_onboarding.py       # Stage 1 checklist & IT dispatch
│   ├── onboarding_day.py       # Stage 2 Day 1 orientation checklist
│   ├── post_onboarding.py      # Stage 3 post-onboarding activities
│   ├── feedback_probation.py   # Stage 4 30/60/90-day probation review
│   ├── existing_associates.py  # Full directory with search & filters
│   ├── associate_details.py    # Detailed profile & document manager
│   ├── dashboard.py            # Plotly analytics dashboard
│   └── reports.py              # Executive reports & export tools
├── services/                   # Business logic repositories
│   ├── associate_service.py    # CRUD & associate filtering engine
│   ├── auth_service.py         # JWT authentication & password hashing
│   ├── import_service.py       # 71-column multi-format file parser & UPSERT
│   ├── progress_service.py     # Dynamic milestone calculator
│   ├── report_service.py       # Analytical metrics aggregator
│   └── activity_service.py     # Centralized audit logger
├── utils/                      # Utilities & helpers
│   ├── constants.py            # App-wide stage & status constants
│   ├── validation.py           # Email, phone, & name validation rules
│   ├── formatting.py           # Date, currency, & display text formatters
│   ├── html_utils.py           # Custom HTML rendering helpers
│   ├── logo_utils.py           # Application logo loader
│   └── logger.py               # Rotating physical app.log file logger
├── assets/                     # UI styling & image assets
│   └── styles.css              # Custom CSS theme stylesheet
├── uploads/                    # Physical document attachment storage
└── tests/                      # Pytest unit & integration test suite
```

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.11 or higher installed.
- PostgreSQL database instance (local or Azure PostgreSQL Flexible Server).

### 2. Installation
```bash
# Clone or navigate to project directory
cd "HR- On Boarding"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your Azure PostgreSQL connection details:
```bash
cp .env.example .env
```

Edit `.env`:
```env
DB_HOST=your-server-name.postgres.database.azure.com
DB_PORT=5432
DB_NAME=employee360
DB_USER=app_user
DB_PASSWORD=your_secure_db_password
DB_SSL_MODE=require
JWT_SECRET=your_super_secret_jwt_key_2026
```

### 4. Running the Application
```bash
streamlit run app.py
```

Default Login Credentials (automatically seeded):
- **Email**: `admin@company.com`
- **Password**: `admin123`

---

## ☁️ Azure Web App Production Deployment Guide

### Step 1: Provision Azure Resources
1. **Azure Database for PostgreSQL Flexible Server**:
   - Create a Flexible Server instance on Azure Portal.
   - Create database `employee360`.
   - In Firewall settings, check **"Allow public access from any Azure service within Azure"**.

2. **Azure App Service (Linux Web App)**:
   - Create a Linux Web App with **Python 3.11** runtime stack.

### Step 2: Configure App Service Environment Variables
In Azure Portal, navigate to **App Service -> Configuration -> Application settings**, and add:
- `DB_HOST`: `your-server.postgres.database.azure.com`
- `DB_PORT`: `5432`
- `DB_NAME`: `employee360`
- `DB_USER`: `app_user`
- `DB_PASSWORD`: `your_secure_db_password`
- `DB_SSL_MODE`: `require`
- `JWT_SECRET`: `your_super_secret_jwt_key_2026`
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`

### Step 3: Configure Startup Command
In Azure Portal, navigate to **App Service -> Configuration -> General settings -> Startup Command**, set:
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

### Step 4: Deploy via Git or Azure CLI
```bash
# Using Azure CLI to deploy zip package
az webapp deploy --resource-group rg-hr-onboarding --name app-hr-onboarding --src-path project.zip --type zip
```

---

## 🧪 Running Unit Tests

```bash
pytest
```
