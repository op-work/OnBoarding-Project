"""
Active Associate Onboarding Workspace View
Renders candidate profile summary, 3-stage milestone stepper, and stage navigation cards.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.employee_profile import render_employee_summary_card
from components.progress import render_stage_stepper
from components.cards import render_stage_card
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from utils.constants import STAGE_PRE_ONBOARDING, STAGE_ONBOARDING_DAY, STAGE_POST_ONBOARDING, STAGE_DESCRIPTIONS
from utils.html_utils import clean_html

def render_onboarding_dashboard_page(db: Session):
    """Renders associate stage workspace."""
    assoc_id = st.session_state.get("selected_associate_id")
    if not assoc_id:
        st.warning("No associate selected. Please select an associate or start a new onboarding.")
        st.button("Select Associate", on_click=lambda: st.session_state.update({"page": "existing_associates"}))
        return

    assoc = AssociateService.get_associate_by_id(db, assoc_id)
    if not assoc:
        st.error("Associate record not found.")
        return

    render_header(
        title="Associate Stage Workspace",
        subtitle=f"Managing onboarding journey for {assoc.full_name}",
        breadcrumbs=["Onboarding Operations", "Associate Workspace", assoc.full_name]
    )

    # Employee Summary Card
    render_employee_summary_card(assoc)

    # Dynamic Overall Progress calculation
    overall = ProgressService.get_overall_progress(db, assoc.id)

    # Completion Banner check
    if overall["overall_status"] == "Completed" or overall["progress_pct"] == 100.0:
        st.markdown(clean_html(f"""
        <div style="
            background: #D1FAE5; border: 2px solid #10B981; border-radius: 12px;
            padding: 24px; text-align: center; margin-bottom: 24px;
        ">
            <h2 style="color: #065F46; margin: 0 0 8px 0;">Onboarding Completed!</h2>
            <p style="color: #047857; margin: 0 0 16px 0;">
                All required onboarding milestones for <strong>{assoc.full_name}</strong> have been successfully verified.
            </p>
        </div>
        """), unsafe_allow_html=True)

    # Visual Onboarding Stepper
    render_stage_stepper(assoc.onboarding_record.current_stage, overall["stages"])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("### Primary Onboarding Stages")

    c1, c2, c3 = st.columns(3)

    with c1:
        s_info = overall["stages"].get(STAGE_PRE_ONBOARDING, {})
        render_stage_card(
            title=STAGE_PRE_ONBOARDING,
            description=STAGE_DESCRIPTIONS[STAGE_PRE_ONBOARDING],
            completed=s_info.get("completed", 0),
            total=s_info.get("total", 6),
            pct=s_info.get("progress_pct", 0.0),
            status=s_info.get("status", "Not Started"),
            page_key="pre_onboarding"
        )

    with c2:
        s_info = overall["stages"].get(STAGE_ONBOARDING_DAY, {})
        render_stage_card(
            title=STAGE_ONBOARDING_DAY,
            description=STAGE_DESCRIPTIONS[STAGE_ONBOARDING_DAY],
            completed=s_info.get("completed", 0),
            total=s_info.get("total", 4),
            pct=s_info.get("progress_pct", 0.0),
            status=s_info.get("status", "Scheduled"),
            page_key="onboarding_day"
        )

    with c3:
        s_info = overall["stages"].get(STAGE_POST_ONBOARDING, {})
        render_stage_card(
            title=STAGE_POST_ONBOARDING,
            description=STAGE_DESCRIPTIONS[STAGE_POST_ONBOARDING],
            completed=s_info.get("completed", 0),
            total=s_info.get("total", 7),
            pct=s_info.get("progress_pct", 0.0),
            status=s_info.get("status", "Not Started"),
            page_key="post_onboarding"
        )
