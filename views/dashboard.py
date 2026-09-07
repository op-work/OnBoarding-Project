"""
Executive Dashboard View
Provides high-level onboarding activity metrics, department distribution charts, and recent candidate milestone summaries.
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

    # Completed Onboard Status Progress Bar (Percentage on the Left)
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; margin-top: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px;">Completed Onboard Status (Average Progress across all joiners)</div>
        {progress_html}
    </div>
    """.format(
        progress_html=render_inline_progress_bar_html(metrics["avg_progress"], color="#10B981", height=10)
    ), unsafe_allow_html=True)

    c_left, c_right = st.columns([1.6, 1])

    with c_left:
        st.markdown("### Onboarding Stage Pipeline")
        stage_data = ReportService.get_stage_breakdown(db)
        if stage_data and sum(stage_data.values()) > 0:
            df_stage = pd.DataFrame(list(stage_data.items()), columns=["Stage", "Candidates"])
            fig_stage = px.bar(
                df_stage,
                x="Stage",
                y="Candidates",
                color="Stage",
                title="Candidates by Active Onboarding Stage",
                text="Candidates",
                color_discrete_sequence=["#1E40AF", "#2563EB", "#3B82F6", "#10B981"]
            )
            fig_stage.update_layout(
                height=300,
                showlegend=False,
                margin=dict(l=20, r=20, t=35, b=20),
                xaxis_title="",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_stage, use_container_width=True)
        else:
            st.info("No active stage pipeline data available.")

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
