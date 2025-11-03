"""
User Management Page
Admin-only page for managing users
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.auth.authentication import Authenticator, Role, Permissions

st.set_page_config(page_title="User Management", page_icon="👥", layout="wide")

# Check authentication
if 'auth' not in st.session_state:
    st.session_state.auth = Authenticator()

auth = st.session_state.auth

if not auth.is_authenticated():
    st.error("🔒 Please login first")
    st.info("Return to the main page to login")
    st.stop()

if not auth.has_permission(Permissions.MANAGE_USERS):
    st.error("🔒 User management requires admin privileges")
    st.info("Only administrators can manage users")
    st.stop()

# Render user info in sidebar
auth.render_user_info()

st.title("👥 User Management")
st.markdown("Manage user accounts and permissions")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View Users", "➕ Create User", "🔑 Change Password", "🗑️ Delete User"])

# Tab 1: View Users
with tab1:
    st.subheader("Current Users")

    users = auth.get_all_users()

    if users:
        import pandas as pd
        df = pd.DataFrame(users)

        # Format the display
        df['created'] = pd.to_datetime(df['created']).dt.strftime('%Y-%m-%d %H:%M')

        # Add role badges
        def format_role(role):
            if role == Role.ADMIN:
                return "👑 Admin"
            else:
                return "👤 User"

        df['role_display'] = df['role'].apply(format_role)

        # Display table
        st.dataframe(
            df[['username', 'name', 'role_display', 'email', 'created']],
            column_config={
                'username': 'Username',
                'name': 'Full Name',
                'role_display': 'Role',
                'email': 'Email',
                'created': 'Created'
            },
            hide_index=True,
            use_container_width=True
        )

        st.caption(f"Total users: {len(users)}")
    else:
        st.info("No users found")

# Tab 2: Create User
with tab2:
    st.subheader("Create New User")

    with st.form("create_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("Username*", help="Unique username for login")
            new_name = st.text_input("Full Name*", help="User's full name")
            new_email = st.text_input("Email", help="User's email address (optional)")

        with col2:
            new_password = st.text_input("Password*", type="password", help="Initial password")
            new_password_confirm = st.text_input("Confirm Password*", type="password")
            new_role = st.selectbox("Role*", [Role.USER, Role.ADMIN],
                                   format_func=lambda x: "👑 Admin" if x == Role.ADMIN else "👤 User")

        submitted = st.form_submit_button("Create User", type="primary", use_container_width=True)

        if submitted:
            # Validation
            if not new_username or not new_name or not new_password:
                st.error("Please fill in all required fields (marked with *)")
            elif new_password != new_password_confirm:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                # Create user
                if auth.create_user(new_username, new_password, new_name, new_role, new_email):
                    st.success(f"✅ User '{new_username}' created successfully!")
                    st.rerun()

# Tab 3: Change Password
with tab3:
    st.subheader("Change User Password")

    users = auth.get_all_users()
    usernames = [u['username'] for u in users]

    with st.form("change_password_form"):
        selected_user = st.selectbox("Select User", usernames)

        # Show current user info
        if selected_user:
            user_info = next((u for u in users if u['username'] == selected_user), None)
            if user_info:
                col1, col2, col3 = st.columns(3)
                col1.metric("Name", user_info['name'])
                col2.metric("Role", "👑 Admin" if user_info['role'] == Role.ADMIN else "👤 User")
                col3.metric("Email", user_info['email'] or "N/A")

        st.divider()

        # Password change
        current_user = auth.get_current_user()

        if selected_user == current_user:
            old_password = st.text_input("Current Password*", type="password")
        else:
            old_password = ""
            st.info("As admin, you can change other users' passwords without knowing their current password")

        new_password = st.text_input("New Password*", type="password")
        new_password_confirm = st.text_input("Confirm New Password*", type="password")

        submitted = st.form_submit_button("Change Password", type="primary", use_container_width=True)

        if submitted:
            if not new_password:
                st.error("Please enter a new password")
            elif new_password != new_password_confirm:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif selected_user == current_user and not old_password:
                st.error("Please enter your current password")
            else:
                if auth.change_password(selected_user, old_password, new_password):
                    st.success(f"✅ Password changed successfully for '{selected_user}'!")

# Tab 4: Delete User
with tab4:
    st.subheader("Delete User")
    st.warning("⚠️ This action cannot be undone!")

    users = auth.get_all_users()
    current_user = auth.get_current_user()

    # Filter out current user
    deletable_users = [u for u in users if u['username'] != current_user]

    if deletable_users:
        with st.form("delete_user_form"):
            usernames = [u['username'] for u in deletable_users]
            selected_user = st.selectbox("Select User to Delete", usernames)

            # Show user info
            if selected_user:
                user_info = next((u for u in deletable_users if u['username'] == selected_user), None)
                if user_info:
                    st.info(f"""
                    **User Information:**
                    - **Username:** {user_info['username']}
                    - **Name:** {user_info['name']}
                    - **Role:** {"👑 Admin" if user_info['role'] == Role.ADMIN else "👤 User"}
                    - **Email:** {user_info['email'] or "N/A"}
                    - **Created:** {user_info['created']}
                    """)

            confirm = st.checkbox("I confirm that I want to delete this user")

            submitted = st.form_submit_button("Delete User", type="primary", use_container_width=True)

            if submitted:
                if not confirm:
                    st.error("Please confirm the deletion")
                else:
                    if auth.delete_user(selected_user):
                        st.success(f"✅ User '{selected_user}' deleted successfully!")
                        st.rerun()
    else:
        st.info("No users available to delete (you cannot delete your own account)")

# Statistics
st.divider()
st.subheader("📊 User Statistics")

users = auth.get_all_users()
admin_count = sum(1 for u in users if u['role'] == Role.ADMIN)
user_count = sum(1 for u in users if u['role'] == Role.USER)

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", len(users))
col2.metric("Administrators", admin_count, delta="👑")
col3.metric("Regular Users", user_count, delta="👤")
