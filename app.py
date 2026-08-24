"""
Onboarding Operations Application Router & Entry Point
Initializes page configuration, applies custom styles, creates SQLite database session, and handles dynamic view routing.
"""

import os
import streamlit as st
from config import APP_TITLE, BASE_DIR
from database import init_db, get_db

# Streamlit Page Config
st.set_page_config(
    page_title="Onboarding Operations",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Application CSS
css_file = BASE_DIR / "assets" / "styles.css"
if css_file.exists():
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize SQLite database and seed initial associates if empty
init_db()

# DB session for current request
db = get_db()

# Session State Initialization & Query Parameter Navigation
if "page" in st.query_params:
    requested_page = st.query_params.get("page")
    if requested_page:
        st.session_state["page"] = requested_page
    st.query_params.clear()

if "page" not in st.session_state:
    st.session_state["page"] = "onboarding_selection"

if "selected_associate_id" not in st.session_state:
    st.session_state["selected_associate_id"] = None

# Sidebar Navigation Component
from components.sidebar import render_sidebar
render_sidebar(db)

# Application View Routing Engine
current_page = st.session_state["page"]

if current_page == "onboarding_selection":
    from views.onboarding_selection import render_onboarding_selection_page
    render_onboarding_selection_page(db)

elif current_page == "new_onboarding":
    from views.new_onboarding import render_new_onboarding_page
    render_new_onboarding_page(db)

elif current_page == "onboarding_dashboard":
    from views.onboarding_dashboard import render_onboarding_dashboard_page
    render_onboarding_dashboard_page(db)

elif current_page == "pre_onboarding":
    from views.pre_onboarding import render_pre_onboarding_page
    render_pre_onboarding_page(db)

elif current_page == "onboarding_day":
    from views.onboarding_day import render_onboarding_day_page
    render_onboarding_day_page(db)

elif current_page == "post_onboarding":
    from views.post_onboarding import render_post_onboarding_page
    render_post_onboarding_page(db)

elif current_page == "existing_associates":
    from views.existing_associates import render_existing_associates_page
    render_existing_associates_page(db)

elif current_page == "associate_details":
    from views.associate_details import render_associate_details_page
    render_associate_details_page(db)

elif current_page == "dashboard":
    from views.dashboard import render_dashboard_page
    render_dashboard_page(db)

elif current_page == "reports":
    from views.reports import render_reports_page
    render_reports_page(db)

else:
    from views.onboarding_selection import render_onboarding_selection_page
    render_onboarding_selection_page(db)
