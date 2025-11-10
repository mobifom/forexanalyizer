"""
Authentication and Authorization Module (Database Version)
Handles user login, role-based access control, and session management using SQLite database
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

from ..database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class Role:
    """User roles with permissions"""
    ADMIN = "admin"
    USER = "user"


class Permissions:
    """Permission definitions"""
    VIEW_ANALYSIS = "view_analysis"
    REFRESH_DATA = "refresh_data"
    TRAIN_MODEL = "train_model"
    SCAN_PAIRS = "scan_pairs"
    MANAGE_USERS = "manage_users"
    CHANGE_SETTINGS = "change_settings"


# Role-Permission Mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permissions.VIEW_ANALYSIS,
        Permissions.REFRESH_DATA,
        Permissions.TRAIN_MODEL,
        Permissions.SCAN_PAIRS,
        Permissions.MANAGE_USERS,
        Permissions.CHANGE_SETTINGS
    ],
    Role.USER: [
        Permissions.VIEW_ANALYSIS,
        Permissions.SCAN_PAIRS,
        # Refresh data and training are NOT included for user role
    ]
}


class AuthenticatorDB:
    """Handles authentication and authorization using database"""

    def __init__(self, db_path: str = 'data/users.db'):
        """
        Initialize authenticator with database

        Args:
            db_path: Path to SQLite database
        """
        self.db = DatabaseManager(db_path)
        self._ensure_default_users()

    def _ensure_default_users(self):
        """
        Ensure default admin and user accounts exist
        """
        try:
            # Check if any users exist
            users = self.db.get_all_users()

            if not users:
                logger.info("No users found - creating default users")

                # Create default admin
                success, msg = self.db.create_user(
                    username='admin',
                    password='admin123',
                    name='Administrator',
                    role=Role.ADMIN,
                    email='admin@forexanalyzer.com'
                )
                if success:
                    logger.info("Default admin user created")

                # Create default user
                success, msg = self.db.create_user(
                    username='user',
                    password='user123',
                    name='Demo User',
                    role=Role.USER,
                    email='user@forexanalyzer.com'
                )
                if success:
                    logger.info("Default user created")

        except Exception as e:
            logger.error(f"Error ensuring default users: {e}")

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful
        """
        try:
            success, user_data = self.db.authenticate_user(username, password)

            if success and user_data:
                # Store user info in session
                st.session_state['authenticated'] = True
                st.session_state['user_id'] = user_data['id']
                st.session_state['username'] = user_data['username']
                st.session_state['role'] = user_data['role']
                st.session_state['user_name'] = user_data['name']
                st.session_state['login_time'] = datetime.now()

                logger.info(f"User {username} logged in successfully")
                return True

            logger.warning(f"Failed login attempt for {username}")
            return False

        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    def logout(self):
        """Logout current user"""
        username = st.session_state.get('username', 'Unknown')

        for key in ['authenticated', 'user_id', 'username', 'role', 'user_name', 'login_time']:
            if key in st.session_state:
                del st.session_state[key]

        logger.info(f"User {username} logged out")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    def get_current_user(self) -> Optional[str]:
        """Get current username"""
        return st.session_state.get('username')

    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID"""
        return st.session_state.get('user_id')

    def get_current_role(self) -> Optional[str]:
        """Get current user role"""
        return st.session_state.get('role')

    def has_permission(self, permission: str) -> bool:
        """
        Check if current user has specific permission

        Args:
            permission: Permission to check

        Returns:
            True if user has permission
        """
        if not self.is_authenticated():
            return False

        role = self.get_current_role()
        return permission in ROLE_PERMISSIONS.get(role, [])

    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.get_current_role() == Role.ADMIN

    def create_user(
        self,
        username: str,
        password: str,
        name: str,
        role: str,
        email: str = ''
    ) -> bool:
        """
        Create new user (admin only)

        Args:
            username: Username
            password: Password
            name: Full name
            role: User role
            email: Email address

        Returns:
            True if user created successfully
        """
        if not self.is_admin():
            st.error("Only administrators can create users")
            return False

        success, message = self.db.create_user(username, password, name, role, email)

        if success:
            st.success(message)
        else:
            st.error(message)

        return success

    def delete_user(self, username: str) -> bool:
        """
        Delete user (admin only)

        Args:
            username: Username to delete

        Returns:
            True if user deleted successfully
        """
        if not self.is_admin():
            st.error("Only administrators can delete users")
            return False

        if username == self.get_current_user():
            st.error("Cannot delete your own account")
            return False

        success, message = self.db.delete_user(username)

        if success:
            st.success(message)
        else:
            st.error(message)

        return success

    def change_password(
        self,
        username: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password

        Args:
            username: Username
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully
        """
        # Users can change their own password, admins can change any password
        if username != self.get_current_user() and not self.is_admin():
            st.error("You can only change your own password")
            return False

        # Verify old password if changing own password
        if username == self.get_current_user():
            success, _ = self.db.authenticate_user(username, old_password)
            if not success:
                st.error("Current password is incorrect")
                return False

        # Change password
        success, message = self.db.change_password(username, new_password)

        if success:
            st.success(message)
        else:
            st.error(message)

        return success

    def get_all_users(self) -> List[Dict]:
        """
        Get all users (admin only)

        Returns:
            List of user dictionaries
        """
        if not self.is_admin():
            return []

        try:
            users = self.db.get_all_users()

            # Format for display
            formatted_users = []
            for user in users:
                if user.get('is_active', 1):  # Only show active users
                    formatted_users.append({
                        'username': user['username'],
                        'name': user['name'],
                        'role': user['role'],
                        'email': user.get('email', ''),
                        'created': user['created_at'],
                        'last_login': user.get('last_login', 'Never')
                    })

            return formatted_users

        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def get_audit_log(self, username: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get audit log (admin only)

        Args:
            username: Filter by username (optional)
            limit: Maximum entries to return

        Returns:
            List of audit log entries
        """
        if not self.is_admin():
            return []

        try:
            return self.db.get_audit_log(username, limit)
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []

    def render_login_page(self):
        """Render login page"""
        st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 2rem;
            background-color: #f0f2f6;
            border-radius: 10px;
            margin-top: 5rem;
        }
        .login-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown('<h1 class="login-header">📈 Forex Analyzer Pro</h1>', unsafe_allow_html=True)
            st.markdown('<h3 style="text-align: center;">Login</h3>', unsafe_allow_html=True)

            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("Login", use_container_width=True, type="primary"):
                    if self.login(username, password):
                        st.success(f"Welcome, {st.session_state['user_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

            with col_b:
                if st.button("Reset", use_container_width=True):
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # Show default credentials for demo
            st.info("""
            **Demo Credentials:**

            👤 **Admin Account:**
            - Username: `admin`
            - Password: `admin123`

            👤 **User Account:**
            - Username: `user`
            - Password: `user123`
            """)

    def render_user_info(self):
        """Render user info in sidebar"""
        if self.is_authenticated():
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 User Information")
            st.sidebar.write(f"**Name:** {st.session_state.get('user_name', 'Unknown')}")
            st.sidebar.write(f"**Username:** {self.get_current_user()}")

            role = self.get_current_role()
            role_emoji = "👑" if role == Role.ADMIN else "👤"
            role_color = "#28a745" if role == Role.ADMIN else "#17a2b8"

            st.sidebar.markdown(
                f'<div style="background-color: {role_color}; color: white; '
                f'padding: 0.5rem; border-radius: 5px; text-align: center;">'\
                f'{role_emoji} <b>{role.upper()}</b></div>',
                unsafe_allow_html=True
            )

            # Show session duration
            login_time = st.session_state.get('login_time')
            if login_time:
                duration = datetime.now() - login_time
                st.sidebar.caption(f"Session: {duration.seconds // 60} minutes")

            st.sidebar.markdown("---")

            if st.sidebar.button("🚪 Logout", use_container_width=True):
                self.logout()
                st.rerun()
