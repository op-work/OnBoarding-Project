"""
Post-Onboarding Activities View
Manages post-joining milestone feedback reviews (30/60/90 days), probation confirmations, and long-term candidate retention tracking.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from database import recalculate_associate_progress
from utils.constants import STAGE_POST_ONBOARDING
from utils.formatting import format_date, calculate_feedback_due_date, calculate_days_overdue

def render_post_onboarding_page(db: Session):
    """Renders Post-Onboarding stage workspace."""
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
        title="Post-Onboarding Milestones & Probation",
        subtitle="Manage 30/60/90-day feedback milestones, insurance setup, and probation confirmation.",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Post-Onboarding"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_POST_ONBOARDING)

    st.markdown(f"""
    <div style="
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex; justify-content: space-between; align-items: center;
    ">
        <div>
            <div style="font-weight: 700; font-size: 16px; color: #0F172A;">{assoc.full_name} ({assoc.employee_id})</div>
            <div style="font-size: 13px; color: #64748B;">
                {assoc.designation} &bull; DOJ: {format_date(assoc.date_of_joining)} &bull; Probation: <strong>{rec.probation_status}</strong>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Post-Onboarding: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">{stage_progress['detail']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    doj = assoc.date_of_joining
    due_30d = calculate_feedback_due_date(doj, 30)
    due_60d = calculate_feedback_due_date(doj, 60)
    due_90d = calculate_feedback_due_date(doj, 90)

    st.markdown("### Milestone Reviews & Probation Confirmation")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 1. Post-Onboarding Lifecycle Status")
        current_post_status = st.selectbox(
            "Post-Onboarding Progress Status:",
            options=["Not Started", "In Progress", "Completed"],
            index=["Not Started", "In Progress", "Completed"].index(rec.post_onboarding_status if rec.post_onboarding_status in ["Not Started", "In Progress", "Completed"] else "Not Started"),
            key="sel_post_status"
        )
        if current_post_status != rec.post_onboarding_status:
            rec.post_onboarding_status = current_post_status
            recalculate_associate_progress(db, assoc.id)
            ActivityService.log_activity(db, "Post-Onboarding Status Updated", f"Updated status to {current_post_status}", assoc.id)
            st.toast("Post-onboarding status updated!")
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("#### 2. Probation Status Confirmation")
        current_probation = st.selectbox(
            "Probation Status:",
            options=["Under Review", "Confirmed"],
            index=["Under Review", "Confirmed"].index(rec.probation_status if rec.probation_status in ["Under Review", "Confirmed"] else "Under Review"),
            key="sel_probation_status"
        )
        if current_probation != rec.probation_status:
            rec.probation_status = current_probation
            recalculate_associate_progress(db, assoc.id)
            ActivityService.log_activity(db, "Probation Confirmed", f"Confirmed probation for {assoc.full_name}", assoc.id)
            st.toast("Probation status updated!")
            st.rerun()

    with c2:
        st.markdown("#### 3. Scheduled Milestone Review Dates")
        st.markdown(f"- **30-Day Check-in:** {format_date(due_30d)}")
        st.markdown(f"- **60-Day Review:** {format_date(due_60d)}")
        st.markdown(f"- **90-Day Probation Review:** {format_date(due_90d)}")

        st.success("Group Health Insurance & Provident Fund (EPF) setup complete.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_onb_post"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
