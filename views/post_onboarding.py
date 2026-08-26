"""
Post-Onboarding Activities View
Manages post-joining milestone feedback reviews (1-week, 30/60/90 days), ID card tickets, HRMS document approvals, and insurance/PF processing.
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
from utils.formatting import format_date
from utils.html_utils import clean_html

def render_post_onboarding_page(db: Session):
    """Renders Post-Onboarding stage workspace with specified 7 milestone checklist items."""
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
        title="Post-Onboarding Activities",
        subtitle="Manage ID card creation, HRMS doc approval, insurance & PF processing, and milestone feedback (1-week, 30/60/90 days).",
        breadcrumbs=["Onboarding Operations", assoc.full_name, "Post-Onboarding"]
    )

    stage_progress = ProgressService.get_stage_progress(db, assoc.id, STAGE_POST_ONBOARDING)

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
            <div style="font-size: 14px; font-weight: 700; color: #2563EB;">Post-Onboarding: {stage_progress['status']}</div>
            <div style="font-size: 12px; color: #64748B;">{stage_progress['detail']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Post-Onboarding Stage Progress Bar (7 Stages: 14.3% increments)
    p_col1, p_col2 = st.columns([4, 1])
    with p_col1:
        st.progress(stage_progress['progress_pct'] / 100.0)
    with p_col2:
        st.markdown(f"**{stage_progress['progress_pct']}%** ({stage_progress['completed']}/7 Verified)")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("### Post-Onboarding Milestone Checklist")

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

    # Item 1: Initiate ID Card Creation
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**1. Initiate ID Card Creation**")
            st.caption("Admin & Keka Ticket Generation")
        with c2:
            st.write("Share the associate's details with the Admin for ID card generation. Raise a ticket on keka with the associates name, Employee ID, email ID, blood group, location and grade with the associates’ photo.")
        with c3:
            is_raised1 = rec.post_id_card_status == "Raised"
            st.markdown(render_status_badge("Completed" if is_raised1 else "Not Started"), unsafe_allow_html=True)
            sel1 = st.selectbox(
                "ID Card Ticket Status:",
                options=["Not Raised", "Raised"],
                index=1 if is_raised1 else 0,
                key="sel_post_id_card",
                label_visibility="collapsed"
            )
            if sel1 != rec.post_id_card_status:
                rec.post_id_card_status = sel1
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"Initiate ID Card Creation set to {sel1}", assoc.id)
                st.toast("ID Card ticket status updated!")
                st.rerun()

    # Item 2: Complete HRMS Documentation
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**2. Complete HRMS Documentation**")
            st.caption("Keka Document Verification & Folder Upload")
        with c2:
            st.markdown("""
            - Verify and approve the associate's details and uploaded documents in Keka.
            - Upload all approved documents to the associate's designated folder. Identity documents, Education Documents, KAI Documents, Previous Experience.
            """)
        with c3:
            is_approved2 = rec.post_hrms_doc_status == "Approved"
            st.markdown(render_status_badge("Completed" if is_approved2 else "Not Started"), unsafe_allow_html=True)
            sel2 = st.selectbox(
                "HRMS Doc Approval Status:",
                options=["Pending Approval", "Approved"],
                index=1 if is_approved2 else 0,
                key="sel_post_hrms_doc",
                label_visibility="collapsed"
            )
            if sel2 != rec.post_hrms_doc_status:
                rec.post_hrms_doc_status = sel2
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"Complete HRMS Documentation set to {sel2}", assoc.id)
                st.toast("HRMS documentation status updated!")
                st.rerun()

    # Item 3: One-Week Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**3. One-Week Feedback**")
            st.caption("1-Week Candidate Check-in")
        with c2:
            st.write("Send the onboarding feedback form after one week of joining over mail.")
        with c3:
            is_done3 = bool(rec.post_feedback_1week)
            st.markdown(render_status_badge("Completed" if is_done3 else "Not Started"), unsafe_allow_html=True)
            chk3 = st.checkbox("Completed", value=is_done3, key="chk_post_fb_1week")
            if chk3 != is_done3:
                rec.post_feedback_1week = chk3
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"One-Week Feedback set to {chk3}", assoc.id)
                st.toast("Post-onboarding status updated!")
                st.rerun()

    # Item 4: Insurance & PF Processing
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**4. Insurance & PF Processing**")
            st.caption("Monthly Insurance & EPF Handover")
        with c2:
            st.markdown("""
            At the end of the month, share the associate's details with:
            - Insurance SPOC – Employee ID, Name, relationship, dob, gender, sum insured, doj
            - PF (Provident Fund) processing
            """)
        with c3:
            is_done4 = bool(rec.post_insurance_pf)
            st.markdown(render_status_badge("Completed" if is_done4 else "Not Started"), unsafe_allow_html=True)
            chk4 = st.checkbox("Completed", value=is_done4, key="chk_post_insurance_pf")
            if chk4 != is_done4:
                rec.post_insurance_pf = chk4
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"Insurance & PF Processing set to {chk4}", assoc.id)
                st.toast("Post-onboarding status updated!")
                st.rerun()

    # Item 5: 30-Day Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**5. 30-Day Feedback**")
            st.caption("1-Month Onboarding Survey")
        with c2:
            st.write("Send the 30-day feedback form to the associate over mail.")
        with c3:
            is_done5 = bool(rec.post_feedback_30days)
            st.markdown(render_status_badge("Completed" if is_done5 else "Not Started"), unsafe_allow_html=True)
            chk5 = st.checkbox("Completed", value=is_done5, key="chk_post_fb_30d")
            if chk5 != is_done5:
                rec.post_feedback_30days = chk5
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"30-Day Feedback set to {chk5}", assoc.id)
                st.toast("Post-onboarding status updated!")
                st.rerun()

    # Item 6: 60-Day Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**6. 60-Day Feedback**")
            st.caption("2-Month Onboarding Survey")
        with c2:
            st.write("Send the 60-day feedback form to the associate over mail.")
        with c3:
            is_done6 = bool(rec.post_feedback_60days)
            st.markdown(render_status_badge("Completed" if is_done6 else "Not Started"), unsafe_allow_html=True)
            chk6 = st.checkbox("Completed", value=is_done6, key="chk_post_fb_60d")
            if chk6 != is_done6:
                rec.post_feedback_60days = chk6
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"60-Day Feedback set to {chk6}", assoc.id)
                st.toast("Post-onboarding status updated!")
                st.rerun()

    # Item 7: 90-Day Feedback
    with st.container(border=True):
        c1, c2, c3 = st.columns([2.5, 4.5, 3])
        with c1:
            st.markdown("**7. 90-Day Feedback**")
            st.caption("3-Month Onboarding Survey")
        with c2:
            st.write("Send the 90-day feedback form to the associate over mail.")
        with c3:
            is_done7 = bool(rec.post_feedback_90days)
            st.markdown(render_status_badge("Completed" if is_done7 else "Not Started"), unsafe_allow_html=True)
            chk7 = st.checkbox("Completed", value=is_done7, key="chk_post_fb_90d")
            if chk7 != is_done7:
                rec.post_feedback_90days = chk7
                recalculate_associate_progress(db, assoc.id)
                ActivityService.log_activity(db, "Post-Onboarding Checklist", f"90-Day Feedback set to {chk7}", assoc.id)
                st.toast("Post-onboarding status updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Associate Workspace", key="btn_back_onb_post", type="primary"):
        st.session_state["page"] = "onboarding_dashboard"
        st.rerun()
