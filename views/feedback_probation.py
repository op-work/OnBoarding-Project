"""
Feedback & Probation Stage View
Manages post-joining 30-day, 60-day, and 90-day milestone feedback surveys and probation completion tracking.
This 4th stage operates with its own individual progress bar and does not affect primary onboarding progress or status.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from database import recalculate_associate_progress
from utils.constants import STAGE_FEEDBACK_PROBATION
from utils.formatting import format_date

def render_feedback_probation_page(db: Session):
    """Renders 4th Stage: Feedback & Probation workspace with individual progress tracking."""
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
        title="Feedback & Probation Workspace",
        subtitle="Manage 30-day, 60-day, 90-day milestone feedback forms and 6-month probation confirmation.",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Feedback & Probation"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_FEEDBACK_PROBATION)

    # Candidate Summary Header
    st.markdown(f"""
    <div style="
        background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex; justify-content: space-between; align-items: center;
    ">
        <div>
            <div style="font-weight: 700; font-size: 16px; color: #0F172A;">{assoc.full_name} ({assoc.employee_id})</div>
            <div style="font-size: 13px; color: #64748B;">
                {assoc.designation} &bull; DOJ: {format_date(assoc.date_of_joining)} &bull; Probation Status: <strong>{rec.probation_status}</strong>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Feedback & Probation: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">{stage_progress['detail']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Individual Stage Progress Bar (4 Milestones: 25% each)
    p_col1, p_col2 = st.columns([4, 1])
    with p_col1:
        st.progress(stage_progress['progress_pct'] / 100.0)
    with p_col2:
        st.markdown(f"**{stage_progress['progress_pct']}%** ({stage_progress['completed']}/4 Verified)")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("### Feedback & Probation Milestone Checklist")

    # Table Header Bar
    st.markdown("""
    <div style="background-color: #1E293B; color: #FFFFFF; padding: 12px 18px; border-radius: 8px; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);">
        <div style="display: flex; align-items: center;">
            <div style="flex: 2.5;">Milestone Activity</div>
            <div style="flex: 4.5;">Details & Information</div>
            <div style="flex: 3; text-align: right;">Status & Update</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Item 1: 30-Day Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**1. 30-Day Feedback**")
            st.caption("1-Month Onboarding Survey")
        with c2:
            st.write("Send the 30-day feedback form to the associate over mail.")
        with c3:
            is_done1 = bool(rec.post_feedback_30days)
            st.markdown(render_status_badge("Completed" if is_done1 else "Not Started"), unsafe_allow_html=True)
            chk1 = st.checkbox("Completed", value=is_done1, key="chk_fp_30d")
            if chk1 != is_done1:
                rec.post_feedback_30days = chk1
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Feedback & Probation Checklist", f"30-Day Feedback set to {chk1}", assoc.id)
                st.toast("30-Day Feedback status updated!")
                st.rerun()

    # Item 2: 60-Day Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**2. 60-Day Feedback**")
            st.caption("2-Month Onboarding Survey")
        with c2:
            st.write("Send the 60-day feedback form to the associate over mail.")
        with c3:
            is_done2 = bool(rec.post_feedback_60days)
            st.markdown(render_status_badge("Completed" if is_done2 else "Not Started"), unsafe_allow_html=True)
            chk2 = st.checkbox("Completed", value=is_done2, key="chk_fp_60d")
            if chk2 != is_done2:
                rec.post_feedback_60days = chk2
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Feedback & Probation Checklist", f"60-Day Feedback set to {chk2}", assoc.id)
                st.toast("60-Day Feedback status updated!")
                st.rerun()

    # Item 3: 90-Day Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**3. 90-Day Feedback**")
            st.caption("3-Month Onboarding Survey")
        with c2:
            st.write("Send the 90-day feedback form to the associate over mail.")
        with c3:
            is_done3 = bool(rec.post_feedback_90days)
            st.markdown(render_status_badge("Completed" if is_done3 else "Not Started"), unsafe_allow_html=True)
            chk3 = st.checkbox("Completed", value=is_done3, key="chk_fp_90d")
            if chk3 != is_done3:
                rec.post_feedback_90days = chk3
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Feedback & Probation Checklist", f"90-Day Feedback set to {chk3}", assoc.id)
                st.toast("90-Day Feedback status updated!")
                st.rerun()

    # Item 4: 6 Months Probation Completed
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**4. 6 Months Probation Completed**")
            st.caption("6-Month Probation Review & Confirmation")
        with c2:
            st.write("Verify completion of 6-month probation period and confirm associate employment status.")
        with c3:
            is_done4 = bool(getattr(rec, "post_probation_completed", False))
            st.markdown(render_status_badge("Completed" if is_done4 else "Not Started"), unsafe_allow_html=True)
            chk4 = st.checkbox("Completed", value=is_done4, key="chk_fp_probation")
            if chk4 != is_done4:
                rec.post_probation_completed = chk4
                if chk4:
                    rec.probation_status = "Confirmed"
                else:
                    rec.probation_status = "Under Review"
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Feedback & Probation Checklist", f"6 Months Probation Completed set to {chk4}", assoc.id)
                st.toast("Probation status updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_fp", type="primary"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
