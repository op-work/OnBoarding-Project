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
from components.progress import render_inline_progress_bar_html
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

    # Completed Onboard Status Progress Bar (Percentage on the Left)
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; margin-top: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px;">Completed Onboard Status (Average Progress across all joiners)</div>
        {progress_html}
    </div>
    """.format(
        progress_html=render_inline_progress_bar_html(metrics["avg_progress"], color="#10B981", height=10)
    ), unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("### Candidates by Department & Progress")
        dept_status_data = ReportService.get_department_status_breakdown(db)
        if dept_status_data and sum(d["Count"] for d in dept_status_data) > 0:
            df_dept = pd.DataFrame(dept_status_data)
            fig_dept = px.bar(
                df_dept,
                x="Department",
                y="Count",
                color="Status",
                title="Department Candidates Divided by Progress Status",
                barmode="stack",
                color_discrete_map={
                    "Completed": "#10B981",
                    "In Progress": "#3B82F6",
                    "Not Started": "#94A3B8"
                },
                text="Count"
            )
            fig_dept.update_layout(
                height=340,
                margin=dict(l=20, r=20, t=35, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis_title="Candidates"
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.info("No department data available.")

    with ch2:
        st.markdown("### Onboarding Status Breakdown")
        if status_data:
            df_st = pd.DataFrame(list(status_data.items()), columns=["Status", "Count"])
            fig_st = px.pie(df_st, names="Status", values="Count", hole=0.4, color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#6B7280"])
            fig_st.update_layout(height=340, margin=dict(l=20, r=20, t=35, b=20))
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
        df_rep.index = range(1, len(df_rep) + 1)
        st.dataframe(df_rep, use_container_width=True)

