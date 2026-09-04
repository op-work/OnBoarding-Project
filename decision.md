# Associate Onboarding Process - Architectural Decisions & Technical Justifications

This document maintains a complete log of all key architectural, technical, and UI/UX design choices made during development.

---

## Decision 1: Tech Stack Choice (Python + Streamlit + Azure PostgreSQL + SQLAlchemy ORM + Plotly)
- **Choice**: Python 3.11+, Streamlit UI framework, Azure PostgreSQL database, SQLAlchemy ORM, Plotly Express charts.
- **Justification**:
  - Full enterprise relational data management backed by Azure PostgreSQL managed database service.
  - SSL/TLS encrypted connection with connection pooling for high concurrency and performance.
  - SQLAlchemy ORM ensures safe, parameterized SQL execution, type hints, and transactional integrity.
  - Plotly integrates natively with Streamlit for enterprise analytics charts.

---

## Decision 2: Single-Page Dynamic Routing Engine (`st.session_state["page"]`)
- **Choice**: Manage page navigation using `st.session_state["page"]` in a single `app.py` entrypoint.
- **Justification**:
  - Preserves session state (e.g. active associate selection, form steps) without full python process re-initializations.
  - Enables custom fixed sidebar, top header breadcrumbs, and instant view changes without page flickers.

---

## Decision 3: Dynamic Task Applicability Engine (`is_applicable` flag)
- **Choice**: Store standard task templates in DB, but set `is_applicable = False` for Online-only shipment tasks when an associate's work mode is Offline.
- **Justification**:
  - Maintains consistent reporting schemas while preventing non-applicable tasks from diluting progress percentages for on-site offline joiners.

---

## Decision 4: Parent Section & Stage Status Derivation
- **Choice**: Derive section and stage status dynamically from child task states rather than manual overrides.
- **Justification**:
  - Enforces data integrity: a section cannot be marked `Completed` if mandatory tasks remain pending.
  - Status rules: 0 completed = `Not Started`, 1 to N-1 = `In Progress`, all completed = `Completed`.

---

## Decision 5: File Storage & Metadata Isolation
- **Choice**: Store uploaded files in `uploads/{associate_id}/` with sanitized filenames, while storing metadata in SQLite `documents` table.
- **Justification**:
  - Prevents path traversal vulnerabilities and filename collisions.
  - Ensures clean separation of binary files and database metadata while preserving full audit trails.

---

## Decision 6: Automatic Demo Seeding
- **Choice**: Automatically populate 5 realistic associate records (Rahul Sharma, Priya Patel, Amit Verma, Sneha Joshi, Arjun Mehta) with genuine task completion states on initial DB launch.
- **Justification**:
  - Provides an immediate, functional prototype suitable for enterprise demonstrations without requiring manual data entry.
