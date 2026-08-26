"""
Pre-Onboarding Stage Operations View
Manages pre-joining formalities, candidate detail verification, IT hardware ticket tracking, and onboarding schedule delivery.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from database import recalculate_associate_progress
from utils.constants import STAGE_PRE_ONBOARDING, WORK_MODE_ONLINE
from utils.formatting import format_date
from utils.html_utils import clean_html

def render_pre_onboarding_page(db: Session):
    """Renders Pre-Onboarding stage workspace with specified 6 milestone checklist items."""
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
        title="Pre-Onboarding Formalities",
        subtitle="Manage pre-joining candidate verification, IT hardware tickets, and onboarding schedule distribution.",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Pre-Onboarding"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_PRE_ONBOARDING)

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
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Pre-Onboarding: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">{stage_progress['detail']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pre-Onboarding Stage Progress Bar
    p_col1, p_col2 = st.columns([4, 1])
    with p_col1:
        st.progress(stage_progress['progress_pct'] / 100.0)
    with p_col2:
        st.markdown(f"**{stage_progress['progress_pct']}%** ({stage_progress['completed']}/6 Verified)")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("### Pre-Onboarding Milestone Checklist")

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

    # Item 1: Receive New Joiner Information
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**1. Receive New Joiner Information**")
            st.caption("TA Information Handover")
        with c2:
            st.write("Receive the onboarding notification and new joiner details from the Talent Acquisition (TA) team.")
        with c3:
            is_done1 = bool(rec.pre_info_received)
            st.markdown(render_status_badge("Completed" if is_done1 else "Not Started"), unsafe_allow_html=True)
            chk1 = st.checkbox("Completed", value=is_done1, key="chk_pre_info")
            if chk1 != is_done1:
                rec.pre_info_received = chk1
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Pre-Onboarding Checklist", f"Receive New Joiner Info set to {chk1}", assoc.id)
                st.toast("Pre-onboarding status updated!")
                st.rerun()

    # Item 2: Connect with the New Joiner
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**2. Connect with the New Joiner**")
            st.caption("Initial Contact & Orientation")
        with c2:
            st.markdown("""
            - Contact the new associate via phone.
            - Verify their personal details. Get their address to send out the assets if the joining is virtual.
            - Inform them about the joining process, required documentation, and onboarding formalities.
            """)
        with c3:
            is_done2 = bool(rec.pre_connect_joiner)
            st.markdown(render_status_badge("Completed" if is_done2 else "Not Started"), unsafe_allow_html=True)
            chk2 = st.checkbox("Completed", value=is_done2, key="chk_pre_connect")
            if chk2 != is_done2:
                rec.pre_connect_joiner = chk2
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Pre-Onboarding Checklist", f"Connect with New Joiner set to {chk2}", assoc.id)
                st.toast("Pre-onboarding status updated!")
                st.rerun()

    # Item 3: Raise IT & Admin Tickets
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**3. Raise IT & Admin Tickets**")
            st.caption("Hardware & Asset Tickets")
        with c2:
            is_online = assoc.work_mode == WORK_MODE_ONLINE
            shipment_bullet = "- Shipment of the laptop and assets if the associate is working remotely." if is_online else "- In-Office Joiner: Assets will be handed over in-person on Onboarding Day at office."
            
            st.markdown(f"""
            Raise ticket to the IT team for:
            - Laptop allocation – Name, contact number, personal mail ID, designation, department, location, reporting manager and address if virtual joiner.
            - Asset provisioning
            {shipment_bullet}
            """)
            if is_online and assoc.asset_shipment_address:
                st.info(f"**Shipment Address:** {assoc.asset_shipment_address}")
        with c3:
            is_raised = rec.pre_it_tickets_status == "Raised"
            st.markdown(render_status_badge("Completed" if is_raised else "Not Started"), unsafe_allow_html=True)
            sel3 = st.selectbox(
                "IT Ticket Status:",
                options=["Not Raised", "Raised"],
                index=1 if is_raised else 0,
                key="sel_pre_it_tickets",
                label_visibility="collapsed"
            )
            if sel3 != rec.pre_it_tickets_status:
                rec.pre_it_tickets_status = sel3
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Pre-Onboarding Checklist", f"IT & Admin Tickets status set to {sel3}", assoc.id)
                st.toast("IT ticket status updated!")
                st.rerun()

    # Item 4: Notify Stakeholders
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**4. Notify Stakeholders**")
            st.caption("Internal Team Notification")
        with c2:
            st.write("Send a new joiner notification to all relevant stakeholders, including the reporting manager, management team, practice heads, IT, Admin, HR, and other applicable teams.")
        with c3:
            is_done4 = bool(rec.pre_notify_stakeholders)
            st.markdown(render_status_badge("Completed" if is_done4 else "Not Started"), unsafe_allow_html=True)
            chk4 = st.checkbox("Completed", value=is_done4, key="chk_pre_notify")
            if chk4 != is_done4:
                rec.pre_notify_stakeholders = chk4
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Pre-Onboarding Checklist", f"Notify Stakeholders set to {chk4}", assoc.id)
                st.toast("Pre-onboarding status updated!")
                st.rerun()

    # Item 5: Prepare the Onboarding Schedule
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**5. Prepare the Onboarding Schedule**")
            st.caption("Agenda & Meeting Invites")
        with c2:
            st.markdown("""
            - Create a detailed onboarding schedule in mail with the given format.
            - Send meeting invites to all respective points of contact involved in the onboarding process.
            """)
        with c3:
            is_done5 = bool(rec.pre_prepare_schedule)
            st.markdown(render_status_badge("Completed" if is_done5 else "Not Started"), unsafe_allow_html=True)
            chk5 = st.checkbox("Completed", value=is_done5, key="chk_pre_prepare")
            if chk5 != is_done5:
                rec.pre_prepare_schedule = chk5
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Pre-Onboarding Checklist", f"Prepare Onboarding Schedule set to {chk5}", assoc.id)
                st.toast("Pre-onboarding status updated!")
                st.rerun()

    # Item 6: Share the Onboarding Schedule
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**6. Share the Onboarding Schedule**")
            st.caption("Candidate Communication")
        with c2:
            st.write("Send the finalized onboarding schedule to the new associate along with joining instructions.")
        with c3:
            is_done6 = bool(rec.pre_share_schedule)
            st.markdown(render_status_badge("Completed" if is_done6 else "Not Started"), unsafe_allow_html=True)
            chk6 = st.checkbox("Completed", value=is_done6, key="chk_pre_share")
            if chk6 != is_done6:
                rec.pre_share_schedule = chk6
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Pre-Onboarding Checklist", f"Share Onboarding Schedule set to {chk6}", assoc.id)
                st.toast("Pre-onboarding status updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_onb_pre", type="primary"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
