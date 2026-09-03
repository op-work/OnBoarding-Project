"""
Sidebar Navigation Component
Renders company branding, top-left logo, active candidate indicator, and main navigation menu.
"""

import streamlit as st
from utils.html_utils import clean_html
from utils.logo_utils import get_logo_data_uri

def render_sidebar(db=None):
    """Renders the main application sidebar navigation."""
    with st.sidebar:
        logo_uri = get_logo_data_uri()
        st.markdown(clean_html(f"""
        <div style="padding: 0 0 12px 0; margin-top: 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
            <div style="background: #FFFFFF; padding: 10px 14px; border-radius: 10px; border: 1px solid #E2E8F0; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05); margin-bottom: 12px; text-align: left;">
                <img src="{logo_uri}" alt="Company Logo" class="sidebar-company-logo" style="height: auto; max-height: 70px; width: 100%; max-width: 250px; object-fit: contain; object-position: left center;" />
            </div>
            <div style="font-size: 18px; font-weight: 800; color: #1E40AF;">
                Onboarding Operations
            </div>
        </div>
        """), unsafe_allow_html=True)


        current_page = st.session_state.get("page", "onboarding_selection")
        assoc_id = st.session_state.get("selected_associate_id")

        if assoc_id and db:
            from services.associate_service import AssociateService
            current_assoc = AssociateService.get_associate_by_id(db, assoc_id)
            if current_assoc:
                st.markdown(clean_html(f"""
                <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 10px; margin-bottom: 16px; font-size: 12px;">
                    <div style="color: #1E40AF; font-weight: 700;">Active Associate</div>
                    <div style="color: #1E293B; font-weight: 600;">{current_assoc.full_name}</div>
                    <div style="color: #64748B;">{current_assoc.designation}</div>
                </div>
                """), unsafe_allow_html=True)
                if st.button("Active Stage Hub", use_container_width=True, type="primary"):
                    st.session_state["page"] = "onboarding_dashboard"
                    st.rerun()

        st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; margin: 12px 0 6px 0; text-transform: uppercase;'>MAIN NAVIGATION</div>", unsafe_allow_html=True)

        nav_items = [
            ("Home", "onboarding_selection"),
            ("Dashboard", "dashboard"),
            ("Existing Associates", "existing_associates"),
            ("New Onboarding", "new_onboarding"),
            ("Reports & Analytics", "reports"),
        ]

        for label, page_key in nav_items:
            is_selected = (current_page == page_key)
            btn_type = "primary" if is_selected else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state["page"] = page_key
                st.rerun()

        # Render Logged In User Profile & Logout Option
        user = st.session_state.get("user")
        if user:
            st.markdown("<div style='margin-top: 24px; border-top: 1px solid #E2E8F0; padding-top: 16px;'></div>", unsafe_allow_html=True)
            st.markdown(clean_html(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px;">Logged In User</div>
                <div style="color: #0F172A; font-weight: 700; font-size: 13px;">{user.get('name', 'User')}</div>
                <div style="color: #64748B; font-size: 11px; word-break: break-all;">{user.get('email', '')}</div>
                <div style="margin-top: 6px;"><span style="background: #DBEAFE; color: #1E40AF; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700;">{user.get('role', 'HR Admin')}</span></div>
            </div>
            """), unsafe_allow_html=True)

            if st.button("Sign Out", key="sidebar_logout_btn", use_container_width=True):

                st.session_state["authenticated"] = False
                st.session_state["user"] = None
                st.session_state["selected_associate_id"] = None
                st.session_state["page"] = "onboarding_selection"
                st.rerun()

