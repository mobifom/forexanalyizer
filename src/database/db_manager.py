"""
Database Manager for User Authentication
Stores user account details in SQLite database instead of YAML files
"""

import sqlite3
import bcrypt
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for user accounts"""

    def __init__(self, db_path: str = 'data/users.db'):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"Database initialized at {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection

        Returns:
            SQLite connection object
        """
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TEXT
                )
            ''')

            # Create sessions table (for tracking active sessions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_username
                ON users(username)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_token
                ON user_sessions(session_token)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp
                ON audit_log(timestamp)
            ''')

            conn.commit()
            logger.info("Database tables created successfully")

        except Exception as e:
            conn.rollback()
            logger.error(f"Error initializing database: {e}")
            raise

        finally:
            conn.close()

    def create_user(
        self,
        username: str,
        password: str,
        name: str,
        role: str,
        email: str = ''
    ) -> Tuple[bool, str]:
        """
        Create a new user

        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            name: Full name
            role: User role (admin/user)
            email: Email address (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Hash password
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            # Get current timestamp
            now = datetime.now().isoformat()

            # Insert user
            cursor.execute('''
                INSERT INTO users (
                    username, password_hash, name, email, role,
                    created_at, updated_at, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (username, password_hash, name, email, role, now, now))

            user_id = cursor.lastrowid

            # Log action
            self._log_action(cursor, user_id, 'USER_CREATED', f'User {username} created')

            conn.commit()
            logger.info(f"User {username} created successfully")
            return True, f"User '{username}' created successfully"

        except sqlite3.IntegrityError:
            conn.rollback()
            logger.warning(f"User {username} already exists")
            return False, f"User '{username}' already exists"

        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating user: {e}")
            return False, f"Error creating user: {str(e)}"

        finally:
            conn.close()

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authenticate a user

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success: bool, user_data: Dict or None)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get user
            cursor.execute('''
                SELECT id, username, password_hash, name, email, role,
                       is_active, failed_login_attempts, locked_until
                FROM users
                WHERE username = ?
            ''', (username,))

            row = cursor.fetchone()

            if not row:
                logger.warning(f"Login attempt for non-existent user: {username}")
                return False, None

            user_id = row['id']
            password_hash = row['password_hash']
            is_active = row['is_active']
            failed_attempts = row['failed_login_attempts']
            locked_until = row['locked_until']

            # Check if user is active
            if not is_active:
                logger.warning(f"Login attempt for inactive user: {username}")
                return False, None

            # Check if account is locked
            if locked_until:
                lock_time = datetime.fromisoformat(locked_until)
                if datetime.now() < lock_time:
                    logger.warning(f"Login attempt for locked user: {username}")
                    return False, None
                else:
                    # Unlock account
                    cursor.execute('''
                        UPDATE users
                        SET locked_until = NULL, failed_login_attempts = 0
                        WHERE id = ?
                    ''', (user_id,))

            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                # Success - reset failed attempts and update last login
                now = datetime.now().isoformat()
                cursor.execute('''
                    UPDATE users
                    SET last_login = ?, failed_login_attempts = 0
                    WHERE id = ?
                ''', (now, user_id))

                # Log successful login
                self._log_action(cursor, user_id, 'LOGIN_SUCCESS', f'User {username} logged in')

                conn.commit()

                # Return user data
                user_data = {
                    'id': row['id'],
                    'username': row['username'],
                    'name': row['name'],
                    'email': row['email'],
                    'role': row['role']
                }

                logger.info(f"User {username} authenticated successfully")
                return True, user_data

            else:
                # Failed - increment failed attempts
                new_failed_attempts = failed_attempts + 1

                # Lock account after 5 failed attempts
                if new_failed_attempts >= 5:
                    lock_until = datetime.now()
                    # Lock for 30 minutes
                    from datetime import timedelta
                    lock_until = (lock_until + timedelta(minutes=30)).isoformat()

                    cursor.execute('''
                        UPDATE users
                        SET failed_login_attempts = ?,
                            locked_until = ?
                        WHERE id = ?
                    ''', (new_failed_attempts, lock_until, user_id))

                    logger.warning(f"Account locked for user: {username}")
                else:
                    cursor.execute('''
                        UPDATE users
                        SET failed_login_attempts = ?
                        WHERE id = ?
                    ''', (new_failed_attempts, user_id))

                # Log failed login
                self._log_action(cursor, user_id, 'LOGIN_FAILED', f'Failed login attempt for {username}')

                conn.commit()

                logger.warning(f"Failed login attempt for user: {username}")
                return False, None

        except Exception as e:
            conn.rollback()
            logger.error(f"Error authenticating user: {e}")
            return False, None

        finally:
            conn.close()

    def get_user(self, username: str) -> Optional[Dict]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            User data dictionary or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, username, name, email, role, created_at,
                       last_login, is_active
                FROM users
                WHERE username = ?
            ''', (username,))

            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        finally:
            conn.close()

    def get_all_users(self) -> List[Dict]:
        """
        Get all users

        Returns:
            List of user dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, username, name, email, role, created_at,
                       last_login, is_active
                FROM users
                ORDER BY created_at DESC
            ''')

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        finally:
            conn.close()

    def update_user(
        self,
        username: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update user details

        Args:
            username: Username
            name: New name (optional)
            email: New email (optional)
            role: New role (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build update query dynamically
            updates = []
            params = []

            if name is not None:
                updates.append('name = ?')
                params.append(name)

            if email is not None:
                updates.append('email = ?')
                params.append(email)

            if role is not None:
                updates.append('role = ?')
                params.append(role)

            if not updates:
                return False, "No fields to update"

            # Add updated_at
            updates.append('updated_at = ?')
            params.append(datetime.now().isoformat())

            # Add username to params
            params.append(username)

            # Execute update
            query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
            cursor.execute(query, params)

            if cursor.rowcount == 0:
                conn.rollback()
                return False, f"User '{username}' not found"

            # Get user ID for logging
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user_id = cursor.fetchone()['id']

            # Log action
            self._log_action(cursor, user_id, 'USER_UPDATED', f'User {username} updated')

            conn.commit()
            logger.info(f"User {username} updated successfully")
            return True, f"User '{username}' updated successfully"

        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating user: {e}")
            return False, f"Error updating user: {str(e)}"

        finally:
            conn.close()

    def change_password(
        self,
        username: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password

        Args:
            username: Username
            new_password: New plain text password

        Returns:
            Tuple of (success: bool, message: str)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Hash new password
            password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            # Update password
            cursor.execute('''
                UPDATE users
                SET password_hash = ?, updated_at = ?
                WHERE username = ?
            ''', (password_hash, datetime.now().isoformat(), username))

            if cursor.rowcount == 0:
                conn.rollback()
                return False, f"User '{username}' not found"

            # Get user ID for logging
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user_id = cursor.fetchone()['id']

            # Log action
            self._log_action(cursor, user_id, 'PASSWORD_CHANGED', f'Password changed for {username}')

            conn.commit()
            logger.info(f"Password changed for user {username}")
            return True, f"Password changed successfully for '{username}'"

        except Exception as e:
            conn.rollback()
            logger.error(f"Error changing password: {e}")
            return False, f"Error changing password: {str(e)}"

        finally:
            conn.close()

    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        Delete a user (soft delete - marks as inactive)

        Args:
            username: Username to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get user ID first
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()

            if not row:
                return False, f"User '{username}' not found"

            user_id = row['id']

            # Soft delete (mark as inactive)
            cursor.execute('''
                UPDATE users
                SET is_active = 0, updated_at = ?
                WHERE username = ?
            ''', (datetime.now().isoformat(), username))

            # Log action
            self._log_action(cursor, user_id, 'USER_DELETED', f'User {username} deactivated')

            conn.commit()
            logger.info(f"User {username} deactivated")
            return True, f"User '{username}' deactivated successfully"

        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting user: {e}")
            return False, f"Error deleting user: {str(e)}"

        finally:
            conn.close()

    def _log_action(
        self,
        cursor: sqlite3.Cursor,
        user_id: Optional[int],
        action: str,
        details: str,
        ip_address: str = None
    ):
        """
        Log an action to audit log

        Args:
            cursor: Database cursor
            user_id: User ID (can be None for system actions)
            action: Action type
            details: Action details
            ip_address: IP address (optional)
        """
        cursor.execute('''
            INSERT INTO audit_log (user_id, action, details, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, details, ip_address, datetime.now().isoformat()))

    def get_audit_log(
        self,
        username: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get audit log entries

        Args:
            username: Filter by username (optional)
            limit: Maximum number of entries

        Returns:
            List of audit log entries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if username:
                cursor.execute('''
                    SELECT a.id, u.username, a.action, a.details,
                           a.ip_address, a.timestamp
                    FROM audit_log a
                    LEFT JOIN users u ON a.user_id = u.id
                    WHERE u.username = ?
                    ORDER BY a.timestamp DESC
                    LIMIT ?
                ''', (username, limit))
            else:
                cursor.execute('''
                    SELECT a.id, u.username, a.action, a.details,
                           a.ip_address, a.timestamp
                    FROM audit_log a
                    LEFT JOIN users u ON a.user_id = u.id
                    ORDER BY a.timestamp DESC
                    LIMIT ?
                ''', (limit,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        finally:
            conn.close()
