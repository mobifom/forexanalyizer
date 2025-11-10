#!/usr/bin/env python3
"""
Migration Script: YAML to SQLite Database
Migrates existing users from config/users.yaml to SQLite database
"""

import yaml
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db_manager import DatabaseManager


def migrate_users():
    """Migrate users from YAML to database"""

    yaml_path = 'config/users.yaml'
    db_path = 'data/users.db'

    print("=" * 60)
    print("USER MIGRATION: YAML → SQLite Database")
    print("=" * 60)

    # Check if YAML file exists
    if not os.path.exists(yaml_path):
        print(f"\n⚠️  No YAML file found at {yaml_path}")
        print("   Creating database with default users...")

        db = DatabaseManager(db_path)
        print("\n✅ Database created with default users (admin/user)")
        print("\n   Default credentials:")
        print("   - Admin: admin / admin123")
        print("   - User: user / user123")
        return

    # Load YAML users
    print(f"\n📂 Loading users from {yaml_path}")

    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            users = config.get('users', {})

        print(f"   Found {len(users)} users in YAML file")

    except Exception as e:
        print(f"\n❌ Error loading YAML file: {e}")
        return

    # Initialize database
    print(f"\n💾 Initializing database at {db_path}")
    db = DatabaseManager(db_path)

    # Check if database already has users
    existing_users = db.get_all_users()
    if existing_users:
        print(f"\n⚠️  Warning: Database already contains {len(existing_users)} users")
        response = input("   Do you want to continue? This will NOT overwrite existing users. (y/n): ")
        if response.lower() != 'y':
            print("\n❌ Migration cancelled")
            return

    # Migrate users
    print(f"\n🔄 Migrating {len(users)} users...")
    print("-" * 60)

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for username, user_data in users.items():
        try:
            # Check if user already exists
            existing = db.get_user(username)
            if existing:
                print(f"⏭️  Skipped: {username} (already exists)")
                skipped_count += 1
                continue

            # Extract user data
            name = user_data.get('name', username)
            password_hash = user_data.get('password')  # Already hashed in YAML
            role = user_data.get('role', 'user')
            email = user_data.get('email', '')

            # Important: YAML passwords are already bcrypt-hashed
            # We need to insert them directly without re-hashing

            # Use raw SQL to insert with existing hash
            conn = db._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO users (
                    username, password_hash, name, email, role,
                    created_at, updated_at, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (username, password_hash, name, email, role, now, now))

            # Log the migration
            user_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'USER_MIGRATED', f'Migrated from YAML', now))

            conn.commit()
            conn.close()

            print(f"✅ Migrated: {username} ({role})")
            migrated_count += 1

        except Exception as e:
            print(f"❌ Error migrating {username}: {e}")
            error_count += 1

    # Summary
    print("-" * 60)
    print("\n📊 Migration Summary:")
    print(f"   ✅ Migrated: {migrated_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")

    # Backup YAML file
    if migrated_count > 0:
        backup_path = f"{yaml_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(yaml_path, backup_path)
            print(f"\n💾 Backup created: {backup_path}")
        except Exception as e:
            print(f"\n⚠️  Could not create backup: {e}")

    print("\n✅ Migration complete!")
    print("\n📝 Next steps:")
    print("   1. Test login with migrated users")
    print("   2. If everything works, you can delete config/users.yaml")
    print("   3. The app will now use the SQLite database")
    print("\n💡 Database location: data/users.db")


if __name__ == '__main__':
    try:
        migrate_users()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
