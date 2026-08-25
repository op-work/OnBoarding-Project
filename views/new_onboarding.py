"""
New Associate Onboarding Registration View
Multi-step form for registering candidate profile details, work mode selection, IT shipment address, and initializing stage milestones.
"""

import datetime
import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from services.associate_service import AssociateService
from utils.validation import validate_associate_form
from utils.constants import DEPARTMENTS, LOCATIONS, GRADES, WORK_MODES, WORK_MODE_ONLINE

def render_new_onboarding_page(db: Session):
    """Renders new associate onboarding creation view."""
    render_header(
        title="New Associate Registration",
        subtitle="Collect associate details, work mode, and initialize onboarding milestone record.",
        breadcrumbs=["Onboarding Operations", "New Onboarding"]
    )

    if "form_step" not in st.session_state:
        st.session_state["form_step"] = 1  # 1: Details Form, 2: Review Screen

    if "new_assoc_form_data" not in st.session_state:
        st.session_state["new_assoc_form_data"] = {}

    form_data = st.session_state["new_assoc_form_data"]

    if st.session_state["form_step"] == 1:
        st.markdown("### Step 1: Associate & Job Information")

        st.markdown("#### 1. Personal & Contact Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            first_name = st.text_input("First Name / Associate Name *", value=form_data.get("first_name", ""))
        with c2:
            last_name = st.text_input("Last Name *", value=form_data.get("last_name", ""))
        with c3:
            preferred_name = st.text_input("Preferred Name", value=form_data.get("preferred_name", ""))

        c4, c5, c6 = st.columns(3)
        with c4:
            personal_email = st.text_input("Personal Email *", value=form_data.get("personal_email", ""))
        with c5:
            phone = st.text_input("Phone Number *", value=form_data.get("phone", ""))
        with c6:
            default_dob = form_data.get("date_of_birth") or datetime.date(2018, 1, 1)
            dob = st.date_input(
                "Date of Birth",
                value=default_dob,
                min_value=datetime.date(1950, 1, 1),
                max_value=datetime.date(2035, 12, 31)
            )

        c7, c8, c9 = st.columns(3)
        with c7:
            address = st.text_area("Address", value=form_data.get("address", ""), height=68)
        with c8:
            city = st.text_input("City", value=form_data.get("city", ""))
            state = st.text_input("State / Province", value=form_data.get("state", ""))
        with c9:
            postal_code = st.text_input("Postal Code", value=form_data.get("postal_code", ""))
            country = st.text_input("Country", value=form_data.get("country", "India"))

        st.markdown("#### 2. Emergency Contact Information")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            ec_name = st.text_input("Emergency Contact Name", value=form_data.get("emergency_contact_name", ""))
        with ec2:
            ec_phone = st.text_input("Emergency Contact Phone", value=form_data.get("emergency_contact_phone", ""))
        with ec3:
            ec_rel = st.text_input("Relationship", value=form_data.get("emergency_contact_relationship", ""))

        st.markdown("#### 3. Employment & Job Details")
        j1, j2, j3 = st.columns(3)
        with j1:
            designation = st.text_input("Designation / Position *", value=form_data.get("designation", ""))
        with j2:
            department_idx = DEPARTMENTS.index(form_data["department"]) if form_data.get("department") in DEPARTMENTS else 0
            department = st.selectbox("Department *", options=DEPARTMENTS, index=department_idx)
        with j3:
            grade_idx = GRADES.index(form_data["grade"]) if form_data.get("grade") in GRADES else 0
            grade = st.selectbox("Grade", options=GRADES, index=grade_idx)

        j4, j5, j6 = st.columns(3)
        with j4:
            default_doj = form_data.get("date_of_joining") or datetime.date.today()
            doj = st.date_input(
                "Date of Joining *",
                value=default_doj,
                min_value=datetime.date(2018, 1, 1),
                max_value=datetime.date(2035, 12, 31)
            )
        with j5:
            location_idx = LOCATIONS.index(form_data["location"]) if form_data.get("location") in LOCATIONS else 0
            location = st.selectbox("Location *", options=LOCATIONS, index=location_idx)
        with j6:
            reporting_manager = st.text_input("Reporting Manager *", value=form_data.get("reporting_manager", ""))

        j7, j8 = st.columns(2)
        with j7:
            emp_id = st.text_input("Employee / Associate ID (Auto-generated if empty)", value=form_data.get("employee_id", ""))
        with j8:
            work_email = st.text_input("Work Email", value=form_data.get("work_email", ""))

        st.markdown("#### 4. Work Mode & Asset Delivery")
        wm_idx = WORK_MODES.index(form_data["work_mode"]) if form_data.get("work_mode") in WORK_MODES else 0
        work_mode = st.radio("Work Mode *", options=WORK_MODES, horizontal=True, index=wm_idx, key="new_assoc_work_mode")

        asset_shipment_address = ""
        if work_mode == WORK_MODE_ONLINE:
            st.info("Online joiner selected. Laptop and welcome assets will be shipped to the address specified below.")
            asset_shipment_address = st.text_area("Asset Shipment Address *", value=form_data.get("asset_shipment_address", ""))
        else:
            st.info("Offline (In-Office) joiner selected. Laptop and welcome assets will be handed over at reception on Onboarding Day.")

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
            "first_name": first_name,
            "last_name": last_name,
            "preferred_name": preferred_name,
            "personal_email": personal_email,
            "phone": phone,
            "date_of_birth": dob,
            "address": address,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "country": country,
            "emergency_contact_name": ec_name,
            "emergency_contact_phone": ec_phone,
            "emergency_contact_relationship": ec_rel,
            "designation": designation,
            "department": department,
            "grade": grade,
            "date_of_joining": doj,
            "location": location,
            "reporting_manager": reporting_manager,
            "employee_id": emp_id,
            "work_email": work_email,
            "work_mode": work_mode,
            "asset_shipment_address": asset_shipment_address
        }

        if btn_draft:
            if not first_name or not personal_email:
                st.error("First name and personal email are required to save a draft.")
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
            st.markdown(f"**Associate Name:** {data.get('first_name')} {data.get('last_name')}")
            st.markdown(f"**Personal Email:** {data.get('personal_email')}")
            st.markdown(f"**Phone:** {data.get('phone')}")
            st.markdown(f"**Work Mode:** `{data.get('work_mode')}`")
            if data.get("work_mode") == WORK_MODE_ONLINE:
                st.markdown(f"**Shipment Address:** {data.get('asset_shipment_address')}")
        with c2:
            st.markdown(f"**Designation:** {data.get('designation')}")
            st.markdown(f"**Department:** {data.get('department')}")
            st.markdown(f"**Date of Joining:** {data.get('date_of_joining')}")
            st.markdown(f"**Location:** {data.get('location')}")
            st.markdown(f"**Reporting Manager:** {data.get('reporting_manager')}")

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
