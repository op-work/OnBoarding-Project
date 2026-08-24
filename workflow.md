# Associate Onboarding Process - Technical Workflow & Execution Architecture

## 1. System Architecture Overview

The **Associate Onboarding Process** is a modular enterprise Python Streamlit web application. It follows a layered, decoupled service architecture:

```
[ UI Layer: Streamlit App Pages (13 Views) ]
                   │
                   ▼
[ Component Layer: Headers, Sidebar, Cards, Steppers, Interactive Checklists ]
                   │
                   ▼
[ Service Layer: Associate, Task, Progress, Document, Activity, Report Services ]
                   │
                   ▼
[ Database Layer: SQLAlchemy ORM Models & SQLite (data/onboarding.db) ]
                   │
                   ▼
[ File System Storage: Uploaded Documents (uploads/{associate_id}/) ]
```

---

## 2. Dynamic Workflow & Routing Engine

Navigation is managed via Streamlit's `st.session_state["page"]` and `st.session_state["selected_associate_id"]`:

1. **Initial Entry Screen (`onboarding_selection`)**:
   - Displays TWO cards: **NEW JOINER** ("Start New Onboarding") and **EXISTING / OLD JOINER** ("View Existing Associates").
2. **New Joiner Registration (`new_onboarding`)**:
   - Step 1: Form collects associate details, contact, job info, work mode (Online / Offline). Conditional Asset Shipment Address field rendered if Online.
   - Form Validation: Ensures required fields, valid email format, valid phone format, and date fields.
   - Step 2: Review screen displaying all inputs before final creation, requiring review confirmation.
   - On submission: Creates `Associate`, `OnboardingRecord`, standard stage tasks (with conditional `is_applicable`), document checklists, and activity log in SQLite.
3. **Onboarding Dashboard (`onboarding_dashboard`)**:
   - Workspace view for active associate.
   - Renders Employee Summary Card, Dynamic Overall Progress Banner, 3 Primary Stage Cards, Visual Stepper.
   - Automatically displays **# Onboarding Completed** screen when overall progress hits 100%.
4. **Stage Views**:
   - `pre_onboarding`: 5 Sections (Receive TA info, Connect with joiner, IT tickets, Notify stakeholders, Schedule).
   - `onboarding_day`: 4 Sections (Mandatory forms, Employment docs, HR induction guide, Viva Engage announcement).
   - `post_onboarding`: 7 Sections (ID card, HRMS docs verification, 1-week feedback [DOJ+7d], Insurance/PF, 30-day feedback [DOJ+30d], 60-day feedback [DOJ+60d], 90-day feedback [DOJ+90d]).
5. **Management Pages**:
   - `existing_associates`: Search and multi-filter table with "View Details" and "Open Workspace" buttons.
   - `associate_details`: Profile, progress %, stage breakdowns, expandable task logs, activity history.
   - `documents`: Document upload (`st.file_uploader`), storage in `uploads/{associate_id}/`, status approvals (`Approved`, `Rejected`, `Received`).
   - `tasks`: Full task inventory with search, filter, edit, delete capabilities.
   - `dashboard`: High-level management overview with 4 key metrics, recent onboarding list, overdue task highlights, stage charts.
   - `reports`: Plotly visual analytics for departments, onboarding statuses, and progress distributions.
   - `settings`: System configurations saved to DB.

---

## 3. Dynamic Progress & Conditional Applicability Algorithm

- **Task Applicability (`is_applicable`)**:
  - `Online` joiners: All tasks are created with `is_applicable = True`.
  - `Offline` joiners: Asset shipment address collection, laptop shipment, and asset shipment tickets are created with `is_applicable = False`.
- **Dynamic Percentage Calculation**:
  - `total_applicable = COUNT(tasks WHERE associate_id = ID AND is_applicable = True)`
  - `completed_applicable = COUNT(tasks WHERE associate_id = ID AND is_applicable = True AND status = 'Completed')`
  - `progress_pct = (completed_applicable / total_applicable) * 100`
  - Non-applicable tasks are strictly excluded from calculations.
- **Section & Stage Status Derivation**:
  - 0 completed = `Not Started`
  - 1 to N-1 completed = `In Progress`
  - All applicable required tasks completed = `Completed`

---

## 4. Document Storage & Audit Trail

- Files uploaded via `st.file_uploader` are sanitized and stored physically in `uploads/{associate_id}/{sanitized_filename}`.
- Metadata (file name, path, status, upload timestamp, review timestamp) is stored in SQLite `documents` table.
- Every task toggle, file upload, status update, or draft save automatically creates an immutable record in `activity_log`.
