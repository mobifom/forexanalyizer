#!/usr/bin/env python3
"""
Unlock Admin User Script
Removes account lock and resets failed login attempts for the admin user
"""

import sqlite3
from datetime import datetime

def unlock_admin():
    """Unlock the admin user account"""
    db_path = 'data/users.db'

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check current status
        cursor.execute('''
            SELECT username, failed_login_attempts, locked_until, is_active
            FROM users
            WHERE username = 'admin'
        ''')

        admin_user = cursor.fetchone()

        if not admin_user:
            print("❌ Admin user not found in database")
            return False

        print(f"\n📊 Current admin account status:")
        print(f"   Username: {admin_user['username']}")
        print(f"   Failed attempts: {admin_user['failed_login_attempts']}")
        print(f"   Locked until: {admin_user['locked_until'] or 'Not locked'}")
        print(f"   Active: {'Yes' if admin_user['is_active'] else 'No'}")

        # Unlock the account
        cursor.execute('''
            UPDATE users
            SET locked_until = NULL,
                failed_login_attempts = 0,
                is_active = 1,
                updated_at = ?
            WHERE username = 'admin'
        ''', (datetime.now().isoformat(),))

        # Log the action
        cursor.execute('''
            INSERT INTO audit_log (user_id, action, details, timestamp)
            SELECT id, 'ADMIN_UNLOCKED', 'Admin account manually unlocked', ?
            FROM users WHERE username = 'admin'
        ''', (datetime.now().isoformat(),))

        conn.commit()

        print(f"\n✅ Admin account unlocked successfully!")
        print(f"   Failed attempts reset to: 0")
        print(f"   Account lock removed")
        print(f"   Account activated")
        print(f"\nYou can now login with username 'admin'")

        return True

    except Exception as e:
        print(f"\n❌ Error unlocking admin account: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("🔓 Admin Account Unlock Utility")
    print("=" * 50)
    unlock_admin()
