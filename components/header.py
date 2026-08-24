"""
Header Navigation Bar Component
Renders the top application header bar, breadcrumbs, title, date indicator, and top-right clickable company logo.
"""

import datetime
import streamlit as st
from utils.formatting import format_date
from utils.html_utils import clean_html
from utils.logo_utils import get_logo_data_uri

def render_header(title: str, subtitle: str = "", breadcrumbs: list = None, header_date=None):
    """Renders page header title, subtitle, breadcrumbs, date badge, and top-right logo."""
    crumb_html = " &nbsp;/&nbsp; ".join(breadcrumbs) if breadcrumbs else "Onboarding Operations"
    sub_html = f'<div style="font-size: 13px; color: #64748B; margin-top: 2px;">{subtitle}</div>' if subtitle else ''
    logo_uri = get_logo_data_uri()
    
    current_date_str = format_date(header_date or datetime.date.today())

    header_html = f"""
    <div style="background: #FFFFFF; border-bottom: 1px solid #E2E8F0; padding: 16px 24px; margin: -1.5rem -1rem 1.5rem -1rem; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="font-size: 12px; color: #64748B; font-weight: 500; margin-bottom: 2px;">{crumb_html}</div>
            <h1 style="font-size: 22px; font-weight: 800; color: #0F172A; margin: 0;">{title}</h1>
            {sub_html}
        </div>
        <div style="display: flex; align-items: center; gap: 16px; margin-right: 50px;">
            <span style="font-size: 12px; background: #F1F5F9; color: #475569; padding: 6px 12px; border-radius: 20px; font-weight: 600;">{current_date_str}</span>
            <a href="?page=onboarding_selection" target="_self" title="Go to Home Page (Onboarding Selection)" style="display: flex; align-items: center; text-decoration: none;" class="company-header-logo">
                <img src="{logo_uri}" alt="Company Logo" style="height: auto; max-height: 75px; width: auto; max-width: 300px; object-fit: contain;" />
            </a>
        </div>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)
