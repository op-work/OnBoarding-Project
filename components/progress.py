"""
Progress Stepper Component
Renders visual onboarding stage steppers and overall progress bars.
"""

import streamlit as st
from utils.html_utils import clean_html

def render_overall_progress_banner(completed: int, total: int, pct: float):
    """Renders overall progress bar and score banner."""
    st.markdown("### Overall Onboarding Progress")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.progress(pct / 100.0)
    with col2:
        st.markdown(f"<div style='text-align: right; font-weight: 700; font-size: 18px; color: #1E40AF;'>{completed} / {total} ({pct}%)</div>", unsafe_allow_html=True)

def render_stage_stepper(current_stage: str, stage_statuses: dict):
    """Renders visual 3-stage milestone stepper."""
    stages = [
        ("Pre-Onboarding", "pre_onboarding"),
        ("Onboarding Day", "onboarding_day"),
        ("Post-Onboarding", "post_onboarding")
    ]

    html_steps = []
    for idx, (title, page_key) in enumerate(stages, 1):
        status_info = stage_statuses.get(title, {})
        status = status_info.get("status", "Not Started")
        
        is_active = (current_stage == page_key or current_stage == title)
        is_completed = (status == "Completed")

        if is_completed:
            circle_style = "background: #10B981; color: white;"
            icon = "✓"
        elif is_active:
            circle_style = "background: #2563EB; color: white; border: 2px solid #93C5FD;"
            icon = str(idx)
        else:
            circle_style = "background: #E2E8F0; color: #64748B;"
            icon = str(idx)

        html_steps.append(f"""
        <div style="flex: 1; text-align: center; position: relative;">
            <div style="width: 36px; height: 36px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; margin-bottom: 6px; {circle_style}">{icon}</div>
            <div style="font-size: 13px; font-weight: 600; color: #1E293B;">{title}</div>
            <div style="font-size: 11px; color: #64748B;">{status}</div>
        </div>
        """)

    inner_html = "".join(html_steps)
    stepper_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 24px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        {inner_html}
    </div>
    """
    st.markdown(clean_html(stepper_html), unsafe_allow_html=True)
