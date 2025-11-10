#!/usr/bin/env python3
"""
Test Login Script
Test if login credentials work correctly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager


def test_login(username, password):
    """Test login credentials"""

    db_path = 'data/users.db'

    print("=" * 60)
    print("LOGIN TEST")
    print("=" * 60)

    print(f"\nTesting credentials:")
    print(f"  Username: {username}")
    print(f"  Password: {'*' * len(password)}")

    # Check database exists
    if not os.path.exists(db_path):
        print(f"\n❌ Error: Database not found at {db_path}")
        return False

    # Test authentication
    try:
        db = DatabaseManager(db_path)
        success, user_data = db.authenticate_user(username, password)

        if success:
            print("\n✅ LOGIN SUCCESSFUL!")
            print(f"\n   User Details:")
            print(f"   - ID: {user_data['id']}")
            print(f"   - Username: {user_data['username']}")
            print(f"   - Name: {user_data['name']}")
            print(f"   - Email: {user_data['email']}")
            print(f"   - Role: {user_data['role']}")
            return True
        else:
            print("\n❌ LOGIN FAILED!")
            print("\n   Possible reasons:")
            print("   1. Incorrect password")
            print("   2. Account is locked")
            print("   3. Account is inactive")

            # Check account status
            user = db.get_user(username)
            if user:
                print(f"\n   Account Status:")
                print(f"   - Active: {user.get('is_active', 0) == 1}")

                # Check if locked
                conn = db._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT failed_login_attempts, locked_until FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    print(f"   - Failed Attempts: {row[0]}")
                    print(f"   - Locked Until: {row[1] or 'Not locked'}")
                conn.close()
            else:
                print(f"\n   ⚠️ User '{username}' not found in database")

            return False

    except Exception as e:
        print(f"\n❌ Error during login test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Test admin login
    print("\n🔐 Testing ADMIN credentials...")
    admin_success = test_login('admin', 'admin123')

    print("\n" + "-" * 60)

    # Test user login
    print("\n🔐 Testing USER credentials...")
    user_success = test_login('user', 'user123')

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Admin Login: {'✅ PASS' if admin_success else '❌ FAIL'}")
    print(f"User Login:  {'✅ PASS' if user_success else '❌ FAIL'}")
    print("=" * 60)
