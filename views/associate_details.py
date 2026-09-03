"""
Associate Details View
Displays candidate profile information, stage milestone statuses, IT hardware shipment tracking, BGV verification status, and audit history.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.employee_profile import render_employee_summary_card
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from utils.constants import STAGE_PRE_ONBOARDING, STAGE_ONBOARDING_DAY, STAGE_POST_ONBOARDING, STAGE_FEEDBACK_PROBATION
from utils.formatting import format_datetime
from utils.html_utils import clean_html

def render_associate_details_page(db: Session):
    """Renders associate detail profile view."""
    assoc_id = st.session_state.get("selected_associate_id")
    if not assoc_id:
        st.warning("No associate selected.")
        return

    assoc = AssociateService.get_associate_by_id(db, assoc_id)
    if not assoc:
        st.error("Associate record not found.")
        return

    render_header(
        title="Associate Onboarding Overview",
        subtitle=f"Milestone status and lifecycle overview for {assoc.full_name}",
        breadcrumbs=["Associates", assoc.full_name, "Onboarding Details"]
    )

    # Employee Profile Summary Card
    render_employee_summary_card(assoc)

    # Overall Progress Metrics
    overall = ProgressService.get_overall_progress(db, assoc.id)
    st.markdown("### Overall Milestone Progress")
    c_p1, c_p2 = st.columns([4, 1])
    with c_p1:
        st.progress(overall["progress_pct"] / 100.0)
    with c_p2:
        st.markdown(f"**{overall['progress_pct']}% Complete**")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("### Stage Breakdown & Verification")

    stages_map = [
        (STAGE_PRE_ONBOARDING, "pre_onboarding"),
        (STAGE_ONBOARDING_DAY, "onboarding_day"),
        (STAGE_POST_ONBOARDING, "post_onboarding"),
        (STAGE_FEEDBACK_PROBATION, "feedback_probation")
    ]

    for stage_name, page_key in stages_map:
        s_info = overall["stages"].get(stage_name, {})
        badge_html = render_status_badge(s_info.get("status", "Not Started"))

        with st.expander(f"{stage_name} Stage Overview", expanded=True):
            st.markdown(f"**Stage Status:** {badge_html}", unsafe_allow_html=True)
            st.markdown(f"**Details:** {s_info.get('detail', 'N/A')}")

            if st.button(f"Manage {stage_name} Stage", key=f"btn_nav_exp_{page_key}"):
                st.session_state["page"] = page_key
                st.rerun()

    st.markdown("---")
    st.markdown("### Audit Activity History")
    logs = ActivityService.get_activity_history(db, associate_id=assoc.id, limit=20)
    if not logs:
        st.info("No activity recorded yet.")
    else:
        for log in logs:
            log_html = f"""
            <div style="background: #F8FAFC; border-left: 4px solid #2563EB; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;">
                <div style="font-size: 11px; color: #64748B;">{format_datetime(log.created_at)} &bull; {log.performed_by}</div>
                <div style="font-size: 13px; font-weight: 600; color: #0F172A;">{log.action}</div>
                <div style="font-size: 12px; color: #475569;">{log.description}</div>
            </div>
            """
            st.markdown(clean_html(log_html), unsafe_allow_html=True)

