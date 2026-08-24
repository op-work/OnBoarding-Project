"""
Reports & Analytics View
Generates executive reports, milestone progress breakdowns, department distributions, and candidate data tables.
"""

import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from components.header import render_header
from components.cards import render_metric_card
from services.report_service import ReportService
from services.associate_service import AssociateService

def render_reports_page(db: Session):
    """Renders reporting and analytics view."""
    render_header(
        title="Reports & Onboarding Analytics",
        subtitle="Dynamic analytics, department breakdowns, and candidate onboarding status reports.",
        breadcrumbs=["Onboarding Operations", "Reports & Analytics"]
    )

    metrics = ReportService.get_dashboard_metrics(db)
    dept_data = ReportService.get_department_breakdown(db)
    status_data = ReportService.get_status_breakdown(db)

    # Key Metrics Bar
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Associates", str(metrics["total_associates"]), icon="👥", color="#2563EB")
    with c2:
        render_metric_card("Avg Progress", f"{metrics['avg_progress']}%", icon="📊", color="#3B82F6")
    with c3:
        render_metric_card("Completed Joiners", str(metrics["completed_onboarding"]), icon="🎯", color="#10B981")
    with c4:
        render_metric_card("Upcoming Joiners", str(metrics["upcoming_joiners"]), icon="📅", color="#8B5CF6")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("### Candidates by Department")
        if dept_data:
            df_dept = pd.DataFrame(list(dept_data.items()), columns=["Department", "Count"])
            fig_dept = px.bar(df_dept, x="Department", y="Count", color="Department", text="Count")
            fig_dept.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.info("No department data available.")

    with ch2:
        st.markdown("### Onboarding Status Breakdown")
        if status_data:
            df_st = pd.DataFrame(list(status_data.items()), columns=["Status", "Count"])
            fig_st = px.pie(df_st, names="Status", values="Count", hole=0.4, color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#6B7280"])
            fig_st.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_st, use_container_width=True)
        else:
            st.info("No status data available.")

    st.markdown("---")
    st.markdown("### Associate Milestone Status Table")
    associates = AssociateService.search_associates(db)

    report_rows = []
    for a in associates:
        rec = a.onboarding_record
        report_rows.append({
            "Employee ID": a.employee_id,
            "Associate Name": a.full_name,
            "Designation": a.designation,
            "Department": a.department,
            "DOJ": a.date_of_joining,
            "Work Mode": a.work_mode,
            "Progress %": rec.overall_progress if rec else 0.0,
            "Overall Status": rec.overall_status if rec else "Not Started"
        })

    if report_rows:
        df_rep = pd.DataFrame(report_rows)
        st.dataframe(df_rep, use_container_width=True)
