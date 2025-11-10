#!/usr/bin/env python3
"""
Reset Admin Password Script
Resets the admin user password to a new password
"""

import sys
import os
import getpass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager


def reset_admin_password():
    """Reset admin password"""

    db_path = 'data/users.db'

    print("=" * 60)
    print("RESET ADMIN PASSWORD")
    print("=" * 60)

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"\n❌ Error: Database not found at {db_path}")
        print("   Please run the app first to create the database.")
        return

    # Get new password
    print("\n🔑 Enter new admin password:")
    new_password = getpass.getpass("New Password: ")

    if len(new_password) < 6:
        print("\n❌ Error: Password must be at least 6 characters long")
        return

    # Confirm password
    confirm_password = getpass.getpass("Confirm Password: ")

    if new_password != confirm_password:
        print("\n❌ Error: Passwords do not match")
        return

    # Reset password
    try:
        db = DatabaseManager(db_path)
        success, message = db.change_password('admin', new_password)

        if success:
            print(f"\n✅ {message}")
            print("\n📝 Admin password has been reset successfully!")
            print("\n   You can now login with:")
            print("   - Username: admin")
            print(f"   - Password: {new_password}")
        else:
            print(f"\n❌ Error: {message}")

    except Exception as e:
        print(f"\n❌ Error resetting password: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        reset_admin_password()
    except KeyboardInterrupt:
        print("\n\n❌ Password reset cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
