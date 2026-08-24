"""
Associate Profile Summary Component
Renders top associate summary card with personal details, designation, department, work mode, and status badge.
"""

import streamlit as st
from models import Associate
from utils.formatting import format_date
from components.status_badge import render_status_badge
from utils.html_utils import clean_html

def render_employee_summary_card(assoc: Associate):
    """Renders associate profile header card."""
    status_badge = render_status_badge(assoc.status)
    mode_badge = f'<span style="background: #E0E7FF; color: #3730A3; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{assoc.work_mode}</span>'

    html = f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <div>
                <h2 style="margin: 0 0 4px 0; font-size: 20px; color: #0F172A; font-weight: 700;">
                    {assoc.full_name} <span style="font-size: 14px; color: #64748B; font-weight: 400;">({assoc.employee_id})</span>
                </h2>
                <div style="font-size: 14px; color: #2563EB; font-weight: 600;">{assoc.designation} &bull; {assoc.department}</div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                {mode_badge}
                {status_badge}
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; padding-top: 12px; border-top: 1px solid #F1F5F9; font-size: 13px;">
            <div><span style="color: #64748B;">Date of Joining:</span> <strong style="color: #0F172A;">{format_date(assoc.date_of_joining)}</strong></div>
            <div><span style="color: #64748B;">Location:</span> <strong style="color: #0F172A;">{assoc.location}</strong></div>
            <div><span style="color: #64748B;">Reporting Manager:</span> <strong style="color: #0F172A;">{assoc.reporting_manager}</strong></div>
            <div><span style="color: #64748B;">Personal Email:</span> <strong style="color: #0F172A;">{assoc.personal_email}</strong></div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)
