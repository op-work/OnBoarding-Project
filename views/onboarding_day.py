"""
Onboarding Day View
Manages Onboarding Day orientation sessions, mandatory forms, employment document signing, HR induction, and joiner announcements.
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
from utils.html_utils import clean_html

def render_onboarding_day_page(db: Session):
    """Renders Onboarding Day stage workspace with specified 4 milestone checklist items."""
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
        title="Onboarding Day Formalities",
        subtitle="Manage mandatory forms, employment agreement signing, HR induction, and team announcements.",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Onboarding Day"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_ONBOARDING_DAY)

    # Top Candidate Summary Header
    st.markdown(f"""
    <div style="
        background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px;
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
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Onboarding Day: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">{stage_progress['detail']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Onboarding Day Stage Progress Bar (4 Stages: 25% increments)
    p_col1, p_col2 = st.columns([4, 1])
    with p_col1:
        st.progress(stage_progress['progress_pct'] / 100.0)
    with p_col2:
        st.markdown(f"**{stage_progress['progress_pct']}%** ({stage_progress['completed']}/4 Verified)")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("### Onboarding Day Milestone Checklist")

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

    # Item 1: Share Mandatory Forms and Assessments
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**1. Share Mandatory Forms and Assessments**")
            st.caption("Forms & Assessments Handover")
        with c2:
            st.markdown("""
            - Background Verification (BGV) Form – to initiate BGV
            - Bank Account Creation Email – Call the spoc to let him know about new joinings
            - ISMS Assessment – ISMS Orientation video recording link which is on Keka is shared with the associate. An acknowledgement is taken and then he must solve the assessment.
            """)
        with c3:
            is_done1 = bool(rec.day1_mandatory_forms)
            st.markdown(render_status_badge("Completed" if is_done1 else "Not Started"), unsafe_allow_html=True)
            chk1 = st.checkbox("Completed", value=is_done1, key="chk_day1_forms")
            if chk1 != is_done1:
                rec.day1_mandatory_forms = chk1
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Onboarding Day Checklist", f"Share Mandatory Forms & Assessments set to {chk1}", assoc.id)
                st.toast("Onboarding Day status updated!")
                st.rerun()

    # Item 2: Share Employment Documents
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**2. Share Employment Documents**")
            st.caption("Digital Document E-Signing")
        with c2:
            st.markdown("""
            - Non-Disclosure Agreement (NDA) – The NDA must be drafted, and a PDF file has to be uploaded on Signdesk (Melento) for the associate to e-sign it. The E-signature needs his Aadhar details
            - Appointment Letter – The appointment letter must be drafted, and a PDF file must be uploaded on Signdesk (Melento) for the associate to e-sign it. The E-signature needs his Aadhar details
            - Authorization Letter - The authorization letter must be drafted, and a PDF file must be uploaded on Signdesk (Melento) for the associate to e-sign it. The E-signature needs his Aadhar details
            """)
        with c3:
            is_done2 = bool(rec.day1_employment_docs)
            st.markdown(render_status_badge("Completed" if is_done2 else "Not Started"), unsafe_allow_html=True)
            chk2 = st.checkbox("Completed", value=is_done2, key="chk_day1_docs")
            if chk2 != is_done2:
                rec.day1_employment_docs = chk2
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Onboarding Day Checklist", f"Share Employment Documents set to {chk2}", assoc.id)
                st.toast("Onboarding Day status updated!")
                st.rerun()

    # Item 3: Conduct HR Induction
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**3. Conduct HR Induction**")
            st.caption("Orientation & HRMS Walkthrough")
        with c2:
            st.markdown("""
            - Conduct the HR induction session.
            - Walk the associate through the HRMS (Keka) portal. - How to track attendance, fill timesheet, apply for leaves, submit and expense claim, raise a ticket etc.
            """)
        with c3:
            is_done3 = bool(rec.day1_hr_induction)
            st.markdown(render_status_badge("Completed" if is_done3 else "Not Started"), unsafe_allow_html=True)
            chk3 = st.checkbox("Completed", value=is_done3, key="chk_day1_induction")
            if chk3 != is_done3:
                rec.day1_hr_induction = chk3
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Onboarding Day Checklist", f"Conduct HR Induction set to {chk3}", assoc.id)
                st.toast("Onboarding Day status updated!")
                st.rerun()

    # Item 4: Announce the New Joiner
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**4. Announce the New Joiner**")
            st.caption("Engagement & Viva Broadcast")
        with c2:
            st.write("Publish the new joiner announcement on the organization's engagement platform. – Ask them to record a video, place the video in the template and upload on Viva engage.")
        with c3:
            is_done4 = bool(rec.day1_announce_joiner)
            st.markdown(render_status_badge("Completed" if is_done4 else "Not Started"), unsafe_allow_html=True)
            chk4 = st.checkbox("Completed", value=is_done4, key="chk_day1_announce")
            if chk4 != is_done4:
                rec.day1_announce_joiner = chk4
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Onboarding Day Checklist", f"Announce the New Joiner set to {chk4}", assoc.id)
                st.toast("Onboarding Day status updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_onb_day", type="primary"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
