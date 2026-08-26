"""
Existing Associates Directory View
Provides search, filtering, and milestone inspection for registered associate profiles.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from utils.constants import DEPARTMENTS, LOCATIONS, WORK_MODES
from utils.formatting import format_date
from utils.html_utils import clean_html

def render_existing_associates_page(db: Session):
    """Renders existing associate directory view."""
    render_header(
        title="Existing Associates Directory",
        subtitle="Search and view registered associates, check onboarding progress, and manage candidate lifecycles.",
        breadcrumbs=["Onboarding Operations", "Existing Associates"]
    )

    st.markdown("### Search & Filter Associates")
    c_s, c_d, c_l, c_st, c_wm = st.columns([2, 1, 1, 1, 1])

    with c_s:
        search_query = st.text_input("Search Name, ID, Designation, Email", value="")
    with c_d:
        dept_filter = st.selectbox("Department", options=["All"] + DEPARTMENTS)
    with c_l:
        loc_filter = st.selectbox("Location", options=["All"] + LOCATIONS)
    with c_st:
        status_filter = st.selectbox("Status", options=["All", "Not Started", "In Progress", "Completed", "Draft"])
    with c_wm:
        mode_filter = st.selectbox("Work Mode", options=["All"] + WORK_MODES)

    associates = AssociateService.search_associates(
        db,
        search_query=search_query,
        department=dept_filter,
        location=loc_filter,
        status=status_filter,
        work_mode=mode_filter
    )

    st.markdown(f"**Found {len(associates)} associate records**")
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if not associates:
        st.info("No associate records found matching the specified filters.")
        return

    for assoc in associates:
        overall = ProgressService.get_overall_progress(db, assoc.id)
        badge_html = render_status_badge(overall["overall_status"])

        card_html = f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 2;">
                    <h4 style="margin: 0 0 2px 0; color: #0F172A; font-size: 16px;">
                        {assoc.full_name} <span style="font-size: 13px; color: #64748B; font-weight: 400;">({assoc.employee_id})</span>
                    </h4>
                    <div style="font-size: 13px; color: #2563EB; font-weight: 600;">
                        {assoc.designation} &bull; {assoc.department} &bull; {assoc.location}
                    </div>
                </div>
                <div style="flex: 1.5; font-size: 13px; color: #475569;">
                    <div>DOJ: <strong>{format_date(assoc.date_of_joining)}</strong></div>
                    <div>Manager: <strong>{assoc.reporting_manager}</strong></div>
                    <div>Mode: <strong>{assoc.work_mode}</strong></div>
                </div>
                <div style="flex: 1.5; text-align: center;">
                    <div style="font-size: 13px; font-weight: 700; color: #1E40AF; margin-bottom: 4px;">
                        {overall['progress_pct']}% Progress
                    </div>
                    {badge_html}
                </div>
            </div>
        </div>
        """
        st.markdown(clean_html(card_html), unsafe_allow_html=True)

        c_act1, c_act2 = st.columns([1.5, 3.5])
        with c_act1:
            if st.button("View Details", key=f"btn_view_{assoc.id}", use_container_width=True):
                st.session_state["selected_associate_id"] = assoc.id
                st.session_state["page"] = "associate_details"
                st.rerun()
        with c_act2:
            if st.button("Open Stage Workspace", key=f"btn_work_{assoc.id}", type="primary", use_container_width=True):
                st.session_state["selected_associate_id"] = assoc.id
                st.session_state["page"] = "onboarding_dashboard"
                st.rerun()
        st.markdown("<hr style='margin: 8px 0 16px 0; border-top: 1px solid #F1F5F9;' />", unsafe_allow_html=True)
