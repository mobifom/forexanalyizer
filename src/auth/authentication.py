"""
Authentication and Authorization Module
Handles user login, role-based access control, and session management
"""

import streamlit as st
import yaml
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os


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


class Authenticator:
    """Handles authentication and authorization"""

    def __init__(self, config_path: str = 'config/users.yaml'):
        """
        Initialize authenticator

        Args:
            config_path: Path to user configuration file
        """
        self.config_path = config_path
        self.users = self._load_users()

    def _load_users(self) -> Dict:
        """Load users from configuration file"""
        if not os.path.exists(self.config_path):
            # Create default users if file doesn't exist
            return self._create_default_users()

        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config.get('users', {})
        except Exception as e:
            st.error(f"Error loading users: {e}")
            return {}

    def _create_default_users(self) -> Dict:
        """Create default admin and user accounts"""
        default_users = {
            'admin': {
                'name': 'Administrator',
                'password': self._hash_password('admin123'),
                'role': Role.ADMIN,
                'email': 'admin@forexanalyzer.com',
                'created': datetime.now().isoformat()
            },
            'user': {
                'name': 'Demo User',
                'password': self._hash_password('user123'),
                'role': Role.USER,
                'email': 'user@forexanalyzer.com',
                'created': datetime.now().isoformat()
            }
        }

        # Save default users
        self._save_users(default_users)
        return default_users

    def _save_users(self, users: Dict):
        """Save users to configuration file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        config = {'users': users}
        with open(self.config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful
        """
        if username not in self.users:
            return False

        user = self.users[username]
        if self._verify_password(password, user['password']):
            # Store user info in session
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.session_state['role'] = user['role']
            st.session_state['user_name'] = user['name']
            st.session_state['login_time'] = datetime.now()
            return True

        return False

    def logout(self):
        """Logout current user"""
        for key in ['authenticated', 'username', 'role', 'user_name', 'login_time']:
            if key in st.session_state:
                del st.session_state[key]

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    def get_current_user(self) -> Optional[str]:
        """Get current username"""
        return st.session_state.get('username')

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

    def create_user(self, username: str, password: str, name: str, role: str, email: str = '') -> bool:
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

        if username in self.users:
            st.error(f"User '{username}' already exists")
            return False

        self.users[username] = {
            'name': name,
            'password': self._hash_password(password),
            'role': role,
            'email': email,
            'created': datetime.now().isoformat()
        }

        self._save_users(self.users)
        return True

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

        if username not in self.users:
            st.error(f"User '{username}' not found")
            return False

        del self.users[username]
        self._save_users(self.users)
        return True

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
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

        if username not in self.users:
            st.error("User not found")
            return False

        user = self.users[username]

        # Verify old password (skip for admin changing other user's password)
        if username == self.get_current_user():
            if not self._verify_password(old_password, user['password']):
                st.error("Current password is incorrect")
                return False

        # Update password
        user['password'] = self._hash_password(new_password)
        user['password_changed'] = datetime.now().isoformat()

        self._save_users(self.users)
        return True

    def get_all_users(self) -> List[Dict]:
        """
        Get all users (admin only)

        Returns:
            List of user dictionaries
        """
        if not self.is_admin():
            return []

        users_list = []
        for username, user_data in self.users.items():
            users_list.append({
                'username': username,
                'name': user_data['name'],
                'role': user_data['role'],
                'email': user_data.get('email', ''),
                'created': user_data.get('created', '')
            })

        return users_list

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
                f'padding: 0.5rem; border-radius: 5px; text-align: center;">'
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
