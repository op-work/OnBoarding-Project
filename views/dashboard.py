"""
Executive Dashboard View
Provides high-level onboarding activity metrics, department distribution charts, and recent candidate milestone summaries.
"""

import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
from sqlalchemy.orm import Session
from components.header import render_header
from components.cards import render_metric_card
from components.status_badge import render_status_badge
from services.report_service import ReportService
from services.associate_service import AssociateService
from services.progress_service import ProgressService
from utils.formatting import format_date
from utils.html_utils import clean_html

def render_dashboard_page(db: Session):
    """Renders executive onboarding operations dashboard."""
    render_header(
        title="Onboarding Operations Dashboard",
        subtitle="Real-time overview of candidate onboarding lifecycles, milestone completion, and department distributions.",
        breadcrumbs=["Onboarding Operations", "Dashboard"]
    )

    metrics = ReportService.get_dashboard_metrics(db)

    # Top KPI Summary Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Total Associates", str(metrics["total_associates"]), "Registered Joiners", icon="👥", color="#2563EB")
    with m2:
        render_metric_card("Active Onboarding", str(metrics["active_onboarding"]), "In Progress Lifecycle", icon="⚡", color="#3B82F6")
    with m3:
        render_metric_card("Completed Onboarding", str(metrics["completed_onboarding"]), "100% Milestone Completion", icon="🎯", color="#10B981")
    with m4:
        render_metric_card("Upcoming Joiners", str(metrics["upcoming_joiners"]), "Next 14 Days", icon="📅", color="#8B5CF6")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.6, 1])

    with c_left:
        st.markdown("### Recent Associate Activity")
        associates = AssociateService.search_associates(db)[:5]

        for assoc in associates:
            overall = ProgressService.get_overall_progress(db, assoc.id)
            badge_html = render_status_badge(overall["overall_status"])

            card_html = f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #0F172A; font-size: 15px;">{assoc.full_name} <span style="font-size: 12px; color: #64748B;">({assoc.employee_id})</span></div>
                        <div style="font-size: 12px; color: #2563EB;">{assoc.designation} &bull; {assoc.department} &bull; DOJ: {format_date(assoc.date_of_joining)}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 13px; font-weight: 700; color: #1E40AF;">{overall['progress_pct']}% Complete</div>
                        {badge_html}
                    </div>
                </div>
            </div>
            """
            st.markdown(clean_html(card_html), unsafe_allow_html=True)

            if st.button("Open Stage Workspace", key=f"btn_dash_assoc_{assoc.id}"):
                st.session_state["selected_associate_id"] = assoc.id
                st.session_state["page"] = "onboarding_dashboard"
                st.rerun()

    with c_right:
        st.markdown("### Department Distribution")
        dept_data = ReportService.get_department_breakdown(db)
        if dept_data:
            fig = px.pie(
                names=list(dept_data.keys()),
                values=list(dept_data.values()),
                title="Candidates by Department",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig.update_layout(margin=dict(l=20, r=20, t=35, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No department data available.")
