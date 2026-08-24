"""
Onboarding Day View
Manages Onboarding Day orientation sessions, HRMS account setup, welcome announcements, and manager introductions.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from database import recalculate_associate_progress
from utils.constants import STAGE_ONBOARDING_DAY
from utils.formatting import format_date

def render_onboarding_day_page(db: Session):
    """Renders Onboarding Day stage workspace."""
    assoc_id = st.session_state.get("selected_associate_id")
    if not assoc_id:
        st.warning("No associate selected.")
        return

    assoc = AssociateService.get_associate_by_id(db, assoc_id)
    if not assoc:
        st.error("Associate record not found.")
        return

    rec = assoc.onboarding_record

    render_header(
        title="Onboarding Day Orientation",
        subtitle="Manage Onboarding Day orientation sessions, HRMS portal walkthroughs, and manager intros.",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Onboarding Day"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_ONBOARDING_DAY)

    st.markdown(f"""
    <div style="
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex; justify-content: space-between; align-items: center;
    ">
        <div>
            <div style="font-weight: 700; font-size: 16px; color: #0F172A;">{assoc.full_name} ({assoc.employee_id})</div>
            <div style="font-size: 13px; color: #64748B;">
                {assoc.designation} &bull; DOJ: {format_date(assoc.date_of_joining)} &bull; Work Mode: <strong>{assoc.work_mode}</strong>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Onboarding Day Orientation: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">Reporting Manager: {assoc.reporting_manager}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Onboarding Day Orientation Controls")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1. HR Orientation & Induction Session")
        st.caption("Conduct HR induction covering company policies, attendance, and benefits.")
        current_orient_status = st.selectbox(
            "Orientation Session Status:",
            options=["Scheduled", "In Progress", "Completed"],
            index=["Scheduled", "In Progress", "Completed"].index(rec.day1_orientation_status if rec.day1_orientation_status in ["Scheduled", "In Progress", "Completed"] else "Scheduled"),
            key="sel_day1_orient_status"
        )
        if current_orient_status != rec.day1_orientation_status:
            rec.day1_orientation_status = current_orient_status
            recalculate_associate_progress(db, assoc.id)
            ActivityService.log_activity(db, "Onboarding Day Orientation Updated", f"Updated orientation status to {current_orient_status}", assoc.id)
            st.toast("Onboarding Day orientation status updated!")
            st.rerun()

    with col2:
        st.markdown("#### 2. Welcome Announcement & Team Intro")
        st.caption("Publish joiner announcement video and introduce candidate to reporting manager.")
        st.success("Welcome email & team announcement calendar invite scheduled.")

    with st.expander("HR Induction Agenda & HRMS Portal Walkthrough", expanded=True):
        st.markdown("""
        #### HRMS Walkthrough Agenda:
        - Attendance tracking & leave application procedures
        - Weekly timesheet submissions & project allocation
        - Expense reimbursements & benefit enrollment
        - Helpdesk ticket creation for IT and facilities

        #### Code of Conduct & Policies:
        - Security awareness and data privacy compliance
        - Remote work policy and office etiquette
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_onb_day"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
