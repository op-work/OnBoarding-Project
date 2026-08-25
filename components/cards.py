"""
Card UI Components
Provides reusable metric cards and stage progress cards for dashboard views.
"""

import streamlit as st
from components.status_badge import render_status_badge
from utils.html_utils import clean_html

def render_metric_card(title: str, value: str, subtitle: str = "", icon: str = "", color: str = "#2563EB"):
    """Renders an executive metric card with professional icon, key value, and subtitle."""
    sub_html = f'<div style="font-size: 12px; color: #94A3B8;">{subtitle}</div>' if subtitle else ''
    icon_content = icon if icon else "•"
    icon_html = f'<div style="width: 48px; height: 48px; border-radius: 10px; background: {color}15; color: {color}; display: flex; align-items: center; justify-content: center; font-size: 22px;">{icon_content}</div>'
    
    html = f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 16px; margin-bottom: 12px;">
        {icon_html}
        <div>
            <div style="font-size: 13px; color: #64748B; font-weight: 500;">{title}</div>
            <div style="font-size: 22px; font-weight: 700; color: #0F172A; margin: 2px 0;">{value}</div>
            {sub_html}
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)

def render_stage_card(title: str, description: str, completed: int, total: int, pct: float, status: str, page_key: str):
    """Renders a stage overview card with status badge, progress bar, and navigation button."""
    status_badge = render_status_badge(status)
    html = f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px; min-height: 185px; height: 185px; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
                <h3 style="margin: 0; font-size: 18px; color: #0F172A; font-weight: 700;">{title}</h3>
                <p style="margin: 4px 0 12px 0; font-size: 13px; color: #64748B; line-height: 1.4;">{description}</p>
            </div>
            <div>{status_badge}</div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #475569; margin-bottom: 0px;">
            <span>Milestone Status: <strong>{completed} / {total} Verified</strong></span>
            <span style="font-weight: 700; color: #2563EB;">{pct}%</span>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)
    st.progress(pct / 100.0)
    
    if st.button(f"Open {title} Stage", key=f"btn_open_stage_{page_key}", use_container_width=True):
        st.session_state["page"] = page_key
        st.rerun()
