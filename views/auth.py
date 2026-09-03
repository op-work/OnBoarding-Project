"""
Authentication View Component
Renders a 2-column zero-scroll enterprise corporate login portal with JWT password security.
"""

import streamlit as st
from services.auth_service import AuthService
from utils.html_utils import clean_html
from utils.logo_utils import get_logo_data_uri


def render_auth_page(db):
    """
    Renders a 2-column zero-scroll enterprise login landing page.
    """
    # Hide sidebar on authentication screen for full width presentation
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stMainBlockContainer"], .main .block-container {
            max-width: 1200px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
        /* Custom card styling for Auth container */
        .auth-form-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
        }
    </style>
    """, unsafe_allow_html=True)

    logo_uri = get_logo_data_uri()

    # Full Width 2-Column Split Layout
    col_brand, col_form = st.columns([1.1, 1], gap="large")

    with col_brand:
        # Enterprise Brand Showcase Panel Box
        st.markdown(clean_html(f"""
        <div style="background: linear-gradient(145deg, #0F172A 0%, #1E3A8A 100%); padding: 32px 30px; border-radius: 16px; color: #FFFFFF; min-height: 460px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.25);">
            <div>
                <div style="margin-bottom: 20px;">
                    <div style="background: #FFFFFF; display: inline-block; padding: 10px 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);">
                        <img src="{logo_uri}" alt="Company Logo" style="max-height: 50px; width: auto; max-width: 220px; object-fit: contain;" />
                    </div>
                </div>
                <div style="display: inline-block; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #93C5FD; margin-bottom: 12px;">
                    Enterprise HR Operations
                </div>
                <h1 style="font-size: 26px; font-weight: 800; color: #FFFFFF; margin: 0 0 10px 0; line-height: 1.25; letter-spacing: -0.5px;">
                    Onboarding Operations Management
                </h1>
                <p style="font-size: 13px; color: #93C5FD; margin: 0 0 24px 0; line-height: 1.5; font-weight: 400;">
                    Centralized platform for managing associate readiness, IT asset dispatch, background verification, and probation compliance.
                </p>
                <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
                    <div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); padding: 8px 12px; border-radius: 8px; font-size: 12px; color: #E2E8F0; font-weight: 500;">
                        • Automated Milestone Progress & Stage Transitions
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); padding: 8px 12px; border-radius: 8px; font-size: 12px; color: #E2E8F0; font-weight: 500;">
                        • IT Equipment Dispatch & BGV Status Verification
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); padding: 8px 12px; border-radius: 8px; font-size: 12px; color: #E2E8F0; font-weight: 500;">
                        • Real-Time Executive Analytics & Audit Logs
                    </div>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with col_form:
        # Auth Form Container Box
        with st.container(border=True):
            auth_tab1, auth_tab2 = st.tabs(["Sign In", "Register Account"])

            with auth_tab1:
                login_email = st.text_input("Corporate Email", placeholder="e.g. admin@company.com", key="auth_login_email")
                login_password = st.text_input("Password", type="password", placeholder="••••••••", key="auth_login_password")

                if st.button("Sign In to Portal", type="primary", use_container_width=True, key="btn_login_submit"):
                    if not login_email or not login_password:
                        st.error("Please enter both email address and password.")
                    else:
                        success, msg, user = AuthService.authenticate_user(db, login_email, login_password)
                        if success and user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = {
                                "id": user.id,
                                "name": user.full_name,
                                "email": user.email,
                                "role": user.role
                            }
                            st.success("Authentication successful. Redirecting...")
                            st.rerun()
                        else:
                            st.error(msg)

                st.markdown("""
                <div style="margin-top: 16px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 12px; font-size: 12px; color: #475569; box-sizing: border-box; overflow: hidden;">
                    <div style="font-weight: 700; color: #1E293B; margin-bottom: 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">System Demo Credentials</div>
                    <div style="display: flex; flex-direction: column; gap: 4px; font-size: 11px;">
                        <div>• Email: <code style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px; color: #0F172A;">admin@company.com</code></div>
                        <div>• Password: <code style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px; color: #0F172A;">admin123</code></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


            with auth_tab2:
                reg_name = st.text_input("Full Name", placeholder="e.g. Sarah Jenkins", key="auth_reg_name")
                reg_email = st.text_input("Work Email", placeholder="e.g. s.jenkins@company.com", key="auth_reg_email")

                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    reg_pass1 = st.text_input("Password", type="password", placeholder="••••••••", key="auth_reg_pass1")
                with c_p2:
                    reg_pass2 = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="auth_reg_pass2")

                reg_role = st.selectbox("Role Specification", ["HR Admin", "HR Manager", "Talent Acquisition", "IT Operations"], key="auth_reg_role")

                if st.button("Complete Registration", type="primary", use_container_width=True, key="btn_register_submit"):
                    if not reg_name or not reg_email or not reg_pass1:
                        st.error("Please fill in all required registration fields.")
                    elif reg_pass1 != reg_pass2:
                        st.error("Passwords do not match. Please verify both fields.")
                    elif len(reg_pass1) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        success, msg, new_user = AuthService.register_user(
                            db=db,
                            full_name=reg_name,
                            email=reg_email,
                            password=reg_pass1,
                            role=reg_role
                        )
                        if success and new_user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = {
                                "id": new_user.id,
                                "name": new_user.full_name,
                                "email": new_user.email,
                                "role": new_user.role
                            }
                            st.success(f"Account registered successfully for {new_user.full_name}. Redirecting...")
                            st.rerun()
                        else:
                            st.error(msg)
