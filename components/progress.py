"""
Progress Stepper Component
Renders visual onboarding stage steppers and overall progress bars.
"""

import streamlit as st
from utils.html_utils import clean_html

def render_inline_progress_bar_html(pct: float, color: str = "#2563EB", height: int = 8) -> str:
    """Generates an HTML progress bar with the percentage on the left side."""
    safe_pct = max(0.0, min(100.0, float(pct)))
    return f"""
    <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
        <span style="font-size: 12px; font-weight: 700; color: #1E40AF; min-width: 42px; text-align: left;">{safe_pct}%</span>
        <div style="flex: 1; background-color: #E2E8F0; border-radius: 9999px; height: {height}px; overflow: hidden;">
            <div style="width: {safe_pct}%; background-color: {color}; height: 100%; border-radius: 9999px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """

def render_overall_progress_banner(completed: int, total: int, pct: float):
    """Renders overall progress bar and score banner with percentage on the left."""
    st.markdown("### Overall Onboarding Progress")
    safe_pct = max(0.0, min(100.0, float(pct)))
    col1, col2 = st.columns([1.5, 4.5])
    with col1:
        st.markdown(f"<div style='font-weight: 700; font-size: 17px; color: #1E40AF; padding-top: 2px;'>{safe_pct}% ({completed}/{total})</div>", unsafe_allow_html=True)
    with col2:
        st.progress(safe_pct / 100.0)

def render_progress_bar_left_pct(pct: float, label: str = "", completed: int = None, total: int = None):
    """Renders a Streamlit progress bar with the percentage number positioned on the left."""
    safe_pct = max(0.0, min(100.0, float(pct)))
    c_left, c_bar = st.columns([1, 5])
    with c_left:
        count_str = f" ({completed}/{total})" if completed is not None and total is not None else ""
        st.markdown(f"<div style='font-size: 16px; font-weight: 700; color: #1E40AF; padding-top: 2px;'>{safe_pct}%{count_str}</div>", unsafe_allow_html=True)
    with c_bar:
        st.progress(safe_pct / 100.0)
        if label:
            st.caption(label)

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
