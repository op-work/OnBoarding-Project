"""
Pre-Onboarding Stage Operations View
Manages pre-joining formalities, candidate detail verification, IT hardware equipment shipment tracking, and background check initiation.
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
    """Renders Pre-Onboarding stage workspace."""
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
        subtitle="Manage pre-joining candidate verification, IT hardware allocation, and BGV initiation.",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Pre-Onboarding"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_PRE_ONBOARDING)

    # Top summary card
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
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Pre-Onboarding: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">{stage_progress['detail']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Pre-Onboarding Milestone Controls")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 1. Candidate Details & Welcome Call")
        st.caption("Verify personal contact details and conduct initial welcome call.")
        current_pre_status = st.selectbox(
            "Pre-Onboarding Readiness Status:",
            options=["Not Started", "In Progress", "Completed"],
            index=["Not Started", "In Progress", "Completed"].index(rec.pre_onboarding_status if rec.pre_onboarding_status in ["Not Started", "In Progress", "Completed"] else "In Progress"),
            key="sel_pre_status"
        )
        if current_pre_status != rec.pre_onboarding_status:
            rec.pre_onboarding_status = current_pre_status
            recalculate_associate_progress(db, assoc.id)
            ActivityService.log_activity(db, "Pre-Onboarding Status Updated", f"Updated status to {current_pre_status}", assoc.id)
            st.toast("Pre-onboarding status updated!")
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 2. Background Verification (BGV)")
        st.caption("Initiate and audit candidate background check.")
        current_bgv_status = st.selectbox(
            "Background Verification Status:",
            options=["Not Started", "In Progress", "Verified"],
            index=["Not Started", "In Progress", "Verified"].index(rec.bgv_status if rec.bgv_status in ["Not Started", "In Progress", "Verified"] else "In Progress"),
            key="sel_bgv_status"
        )
        if current_bgv_status != rec.bgv_status:
            rec.bgv_status = current_bgv_status
            recalculate_associate_progress(db, assoc.id)
            ActivityService.log_activity(db, "BGV Status Updated", f"Updated background check to {current_bgv_status}", assoc.id)
            st.toast("BGV status updated!")
            st.rerun()

    with c2:
        st.markdown("#### 3. IT Hardware & Laptop Provisioning")
        if assoc.work_mode == WORK_MODE_ONLINE:
            st.info(f"Shipment Address: {assoc.asset_shipment_address or 'Pending Verification'}")
        else:
            st.info("In-Office Joiner: Asset will be handed over at reception on Onboarding Day.")

        current_it_status = st.selectbox(
            "IT Asset Dispatch Status:",
            options=["Pending Dispatch", "Dispatched", "Delivered"],
            index=["Pending Dispatch", "Dispatched", "Delivered"].index(rec.it_equipment_status if rec.it_equipment_status in ["Pending Dispatch", "Dispatched", "Delivered"] else "Pending Dispatch"),
            key="sel_it_status"
        )
        if current_it_status != rec.it_equipment_status:
            rec.it_equipment_status = current_it_status
            recalculate_associate_progress(db, assoc.id)
            ActivityService.log_activity(db, "IT Equipment Status Updated", f"Updated hardware status to {current_it_status}", assoc.id)
            st.toast("IT equipment status updated!")
            st.rerun()

    with st.expander("IT Provisioning Ticket Information", expanded=False):
        st.markdown(f"""
        - **Associate Name:** {assoc.full_name}
        - **Employee ID:** {assoc.employee_id}
        - **Designation:** {assoc.designation}
        - **Department:** {assoc.department}
        - **Work Mode:** {assoc.work_mode}
        - **Reporting Manager:** {assoc.reporting_manager}
        {"- **Shipment Address:** " + str(assoc.asset_shipment_address) if assoc.work_mode == WORK_MODE_ONLINE else ""}
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_onb_pre"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
