"""
New Associate Onboarding Registration View
Streamlined multi-step form for registering candidate profile details based on required 7 fields.
"""

import datetime
import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from services.associate_service import AssociateService
from utils.validation import validate_associate_form
from utils.constants import JOB_LOCATIONS, MODES_OF_JOINING
from utils.formatting import format_date

def render_new_onboarding_page(db: Session):
    """Renders new associate onboarding creation view."""
    render_header(
        title="New Associate Registration",
        subtitle="Fill in candidate details to initialize onboarding milestone record.",
        breadcrumbs=["Onboarding Operations", "New Onboarding"]
    )

    if "form_step" not in st.session_state:
        st.session_state["form_step"] = 1  # 1: Details Form, 2: Review Screen

    if "new_assoc_form_data" not in st.session_state:
        st.session_state["new_assoc_form_data"] = {}

    form_data = st.session_state["new_assoc_form_data"]

    if st.session_state["form_step"] == 1:
        st.markdown("### New Joiner Form")

        c1, c2 = st.columns(2)
        with c1:
            name_as_per_aadhar = st.text_input(
                "Name as per Aadhar *",
                value=form_data.get("name_as_per_aadhar", form_data.get("first_name", "")),
                placeholder="Full Name",
                help="Type the full candidate name exactly as printed on Aadhar card."
            )
        with c2:
            personal_email = st.text_input(
                "Personal Email ID *",
                value=form_data.get("personal_email", ""),
                placeholder="associate@example.com"
            )

        c3, c4 = st.columns(2)
        with c3:
            default_doj = form_data.get("date_of_joining") or datetime.date.today()
            doj = st.date_input(
                "Confirmed Date of Joining *",
                value=default_doj,
                min_value=datetime.date(2018, 1, 1),
                max_value=datetime.date(2035, 12, 31),
                format="DD/MM/YYYY"
            )
        with c4:
            designation = st.text_input(
                "Communicated Designation *",
                value=form_data.get("designation", ""),
                placeholder="e.g. Senior Software Engineer"
            )

        c5, c6 = st.columns(2)
        with c5:
            loc_idx = JOB_LOCATIONS.index(form_data["location"]) if form_data.get("location") in JOB_LOCATIONS else 0
            location = st.selectbox("Job Location *", options=JOB_LOCATIONS, index=loc_idx)
        with c6:
            mode_idx = MODES_OF_JOINING.index(form_data["work_mode"]) if form_data.get("work_mode") in MODES_OF_JOINING else 0
            work_mode = st.selectbox("Mode of Joining *", options=MODES_OF_JOINING, index=mode_idx)

        st.markdown("#### Previous Work Experience")
        is_fresher = st.checkbox(
            "Fresher (Check if candidate has no prior work experience)",
            value=form_data.get("is_fresher", False)
        )

        last_working_day = None
        if not is_fresher:
            default_lwd = form_data.get("last_working_day") or datetime.date.today()
            last_working_day = st.date_input(
                "Last Working Day with Previous Employer *",
                value=default_lwd,
                min_value=datetime.date(2015, 1, 1),
                max_value=datetime.date(2035, 12, 31),
                format="DD/MM/YYYY"
            )

        asset_shipment_address = ""
        if work_mode == "Virtual":
            st.info("Virtual mode selected. Laptop and welcome assets will be shipped to the candidate's address.")
            asset_shipment_address = st.text_area(
                "Associate Address for Asset Delivery *",
                value=form_data.get("asset_shipment_address", ""),
                height=80,
                placeholder="Enter complete delivery address with PIN code"
            )
        else:
            st.info("In-person mode selected. Laptop and welcome assets will be handed over at reception on joining day.")

        st.markdown("<br>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
        with col_b1:
            btn_draft = st.button("Save Draft", use_container_width=True, key="btn_new_assoc_draft")
        with col_b2:
            btn_cancel = st.button("Cancel", use_container_width=True, key="btn_new_assoc_cancel")
        with col_b3:
            btn_continue = st.button("Continue to Review", type="primary", use_container_width=True, key="btn_new_assoc_continue")

        if btn_cancel:
            st.session_state["page"] = "onboarding_selection"
            st.rerun()

        curr_data = {
            "name_as_per_aadhar": name_as_per_aadhar,
            "first_name": name_as_per_aadhar,
            "last_name": "",
            "personal_email": personal_email,
            "date_of_joining": doj,
            "is_fresher": is_fresher,
            "last_working_day": last_working_day,
            "designation": designation,
            "location": location,
            "work_mode": work_mode,
            "asset_shipment_address": asset_shipment_address
        }

        if btn_draft:
            if not name_as_per_aadhar or not personal_email:
                st.error("Name as per Aadhar and personal email are required to save a draft.")
            else:
                assoc = AssociateService.create_associate(db, curr_data, is_draft=True)
                st.success(f"Draft saved for {assoc.full_name}! Employee ID: {assoc.employee_id}")
                st.session_state["selected_associate_id"] = assoc.id
                st.session_state["page"] = "existing_associates"
                st.rerun()

        if btn_continue:
            is_valid, errors = validate_associate_form(curr_data)
            if not is_valid:
                for err in errors.values():
                    st.error(f"{err}")
            else:
                st.session_state["new_assoc_form_data"] = curr_data
                st.session_state["form_step"] = 2
                st.rerun()

    elif st.session_state["form_step"] == 2:
        st.markdown("### Step 2: Review Onboarding Setup Before Submission")

        data = st.session_state["new_assoc_form_data"]

        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h4 style="margin: 0 0 12px 0; color: #1E40AF;">Review Summary</h4>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Name as per Aadhar:** {data.get('name_as_per_aadhar') or data.get('first_name')}")
            st.markdown(f"**Personal Email ID:** {data.get('personal_email')}")
            st.markdown(f"**Confirmed Date of Joining:** {format_date(data.get('date_of_joining'))}")
            if data.get("is_fresher"):
                st.markdown("**Work Experience:** `Fresher`")
            else:
                st.markdown(f"**Last Working Day:** {format_date(data.get('last_working_day'))}")
        with c2:
            st.markdown(f"**Communicated Designation:** {data.get('designation')}")
            st.markdown(f"**Job Location:** {data.get('location')}")
            st.markdown(f"**Mode of Joining:** `{data.get('work_mode')}`")
            if data.get("work_mode") == "Virtual":
                st.markdown(f"**Asset Delivery Address:** {data.get('asset_shipment_address')}")

        st.markdown("---")
        confirm = st.checkbox("I confirm that the associate information and onboarding setup have been reviewed.")

        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("Edit Details", use_container_width=True):
                st.session_state["form_step"] = 1
                st.rerun()
        with b_col2:
            if st.button("Finalize & Create Onboarding", type="primary", use_container_width=True, disabled=not confirm):
                assoc = AssociateService.create_associate(db, data, is_draft=False)
                st.session_state["selected_associate_id"] = assoc.id
                st.session_state["page"] = "onboarding_dashboard"
                st.session_state["form_step"] = 1
                st.session_state["new_assoc_form_data"] = {}
                st.toast(f"Onboarding created for {assoc.full_name}!")
                st.rerun()
