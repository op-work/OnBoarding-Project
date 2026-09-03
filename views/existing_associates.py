"""
Existing Associates Directory View
Provides search, filtering, milestone inspection, and direct 1-step employee data file upload.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from components.status_badge import render_status_badge
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from services.import_service import ImportService
from utils.constants import DEPARTMENTS, LOCATIONS, WORK_MODES
from utils.formatting import format_date
from utils.html_utils import clean_html


def render_existing_associates_page(db: Session):
    """Renders existing associate directory view with 1-step employee data file upload."""
    render_header(
        title="Existing Associates Directory",
        subtitle="Search and view registered associates, check onboarding progress, and upload employee records.",
        breadcrumbs=["Onboarding Operations", "Existing Associates"]
    )

    # Top Header & 1-Step Direct File Upload Bar
    c_head1, c_head2 = st.columns([1.5, 1])
    with c_head1:
        st.markdown("### Registered Associates Directory")
        st.markdown("<p style='font-size: 13px; color: #64748B; margin-top: -8px;'>Manage active employees or upload data directly from your device.</p>", unsafe_allow_html=True)
    with c_head2:
        uploaded_file = st.file_uploader(
            "Upload Employee Data (CSV, Excel, JSON)",
            key="direct_employee_file_uploader",
            help="Select a CSV, Excel (.xlsx/.xls), or JSON file directly from your device."
        )

    # Automatic File Processing & Format Recognition
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name

        # Format Recognition & Validation
        is_supported, format_display_name, detected_ext = ImportService.detect_file_format(file_bytes, file_name)

        if not is_supported:
            st.error(f"File not supported: '{file_name}'. Please upload a valid CSV, Excel (.xlsx/.xls), or JSON file.")
        else:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #2563EB; border-left: 4px solid #1E40AF; border-radius: 12px; padding: 16px 20px; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(37, 99, 235, 0.08);">
                <h4 style="margin: 0 0 4px 0; color: #0F172A; font-size: 15px;">Employee Data Import Preview</h4>
                <p style="margin: 0; font-size: 12px; color: #2563EB; font-weight: 600;">
                    Recognized Format: {format_name}
                </p>
            </div>
            """.format(format_name=format_display_name), unsafe_allow_html=True)

            raw_rows = ImportService.parse_file(file_bytes, file_name)

            if not raw_rows:
                st.error("No valid data rows found in the uploaded file.")
            else:
                valid_records, invalid_records = ImportService.process_and_validate(raw_rows, db)

                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Total Parsed Rows", len(raw_rows))
                with col_m2:
                    st.metric("Ready for Import", len(valid_records))
                with col_m3:
                    st.metric("Duplicate / Skipped", len(invalid_records))

                if valid_records:
                    st.markdown("##### Preview Valid Employee Records")
                    preview_display = []
                    for vr in valid_records[:10]:  # Show first 10 records
                        preview_display.append({
                            "Row #": vr["row_index"],
                            "Employee ID": vr["employee_id"],
                            "Action": "Update Existing" if vr["import_status"] == "Update" else "New Record",
                            "Full Name": vr["full_name"],
                            "Work Email": vr["email"],
                            "Designation": vr["designation"],
                            "Department": vr["department"],
                            "Location": vr["location"],
                            "DOJ": str(vr["date_of_joining"]),
                            "Work Mode": vr["work_mode"]
                        })
                    st.dataframe(preview_display, use_container_width=True)


                if invalid_records:
                    st.warning(f"Found {len(invalid_records)} duplicate or incomplete records that will be skipped:")
                    skipped_display = []
                    for ir in invalid_records:
                        skipped_display.append({
                            "Row #": ir["row_index"],
                            "Full Name": ir["full_name"],
                            "Email": ir["email"],
                            "Issue / Reason": ir["import_issue"]
                        })
                    st.dataframe(skipped_display, use_container_width=True)

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                if valid_records:
                    if st.button(f"Confirm & Ingest {len(valid_records)} Valid Employees", type="primary", use_container_width=True):
                        created = ImportService.ingest_records(db, valid_records)
                        st.success(f"Successfully imported {len(created)} employee records into database!")
                        st.rerun()

    st.markdown("<hr style='margin: 16px 0;' />", unsafe_allow_html=True)

    # Search & Filter Controls
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
