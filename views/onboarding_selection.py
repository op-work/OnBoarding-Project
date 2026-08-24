"""
Onboarding Home View
Landing portal for initiating new candidate onboarding or searching existing associate directories.
"""

import streamlit as st
from sqlalchemy.orm import Session
from components.header import render_header
from utils.html_utils import clean_html

def render_onboarding_selection_page(db: Session):
    """Renders onboarding selection home portal."""
    render_header(
        title="Onboarding Operations Portal",
        subtitle="Manage candidate onboarding journeys from pre-onboarding formalities to post-onboarding confirmations.",
        breadcrumbs=["Onboarding Operations", "Home"]
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(clean_html("""
        <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 16px; padding: 32px 24px; text-align: center; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 64px; height: 64px; border-radius: 50%; background: #DBEAFE; color: #2563EB; font-size: 24px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">NEW</div>
                <h2 style="font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 8px 0;">NEW JOINER</h2>
                <p style="font-size: 14px; color: #64748B; line-height: 1.5; margin-bottom: 24px;">Start a new onboarding process for an associate joining the organization. Collect details, set work mode, and initialize milestone records.</p>
            </div>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Start New Onboarding", key="btn_start_new_onboarding", type="primary", use_container_width=True):
            st.session_state["page"] = "new_onboarding"
            st.rerun()

    with col2:
        st.markdown(clean_html("""
        <div style="background: #FFFFFF; border: 2px solid #64748B; border-radius: 16px; padding: 32px 24px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 64px; height: 64px; border-radius: 50%; background: #F1F5F9; color: #475569; font-size: 24px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">LIST</div>
                <h2 style="font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 8px 0;">EXISTING / OLD JOINER</h2>
                <p style="font-size: 14px; color: #64748B; line-height: 1.5; margin-bottom: 24px;">View registered associates and inspect onboarding statuses, stage progress, and verified milestones.</p>
            </div>
        </div>
        """), unsafe_allow_html=True)
        if st.button("View Existing Associates", key="btn_view_existing_associates", type="secondary", use_container_width=True):
            st.session_state["page"] = "existing_associates"
            st.rerun()
