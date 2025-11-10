# 🗄️ Database Migration Guide - YAML to SQLite

## Overview

The Forex Analyzer has been upgraded from YAML file-based user storage to a robust SQLite database system. This provides better security, scalability, and auditing capabilities.

---

## ✨ What Changed?

### Before (YAML-based)
- ❌ User credentials stored in `config/users.yaml`
- ❌ Limited security features
- ❌ No audit logging
- ❌ No account locking
- ❌ Manual file editing required

### After (Database-based)
- ✅ User credentials stored in SQLite database (`data/users.db`)
- ✅ Enhanced security with bcrypt password hashing
- ✅ Comprehensive audit logging
- ✅ Account locking after failed attempts (5 tries = 30 min lockout)
- ✅ Session tracking
- ✅ Soft delete (users marked inactive, not deleted)
- ✅ Full CRUD operations through UI

---

## 🎯 Key Features

### 1. **Enhanced Security**
- Bcrypt password hashing with salt
- Account locking after 5 failed login attempts
- 30-minute lockout period after account lock
- Session management
- Password change functionality

### 2. **Audit Logging**
- All user actions tracked in `audit_log` table
- Tracks: login attempts, user creation, password changes, etc.
- Timestamps for all actions
- Optional IP address tracking

### 3. **User Management**
- Create/Read/Update/Delete users through GUI
- Change passwords for self or others (admin only)
- View all users and their last login times
- Soft delete (mark inactive instead of hard delete)

### 4. **Database Schema**

#### **users table**
```sql
CREATE TABLE users (
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
```

#### **user_sessions table**
```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

#### **audit_log table**
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

---

## 🚀 Migration Process

### Step 1: Automatic Migration

The system has already been migrated! Here's what happened:

1. **Migration Script Executed**: `migrate_users_to_db.py`
2. **Users Migrated**: 2 users (admin, user)
3. **Backup Created**: `config/users.yaml.backup_20251106_174820`
4. **Database Created**: `data/users.db`

### Step 2: Verify Migration

Check migrated users:
```bash
sqlite3 data/users.db "SELECT username, name, role, created_at FROM users;"
```

Expected output:
```
admin|Administrator|admin|2025-11-06T17:48:20.227020
user|Demo User|user|2025-11-06T17:48:20.227675
```

### Step 3: Test Login

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Test with default credentials:
   - **Admin**: username: `admin`, password: `admin123`
   - **User**: username: `user`, password: `user123`

---

## 📦 File Structure

### New Files Created

```
ForexAnalyzer/
├── src/
│   ├── database/
│   │   ├── __init__.py              # Package initialization
│   │   └── db_manager.py            # Database operations (600+ lines)
│   └── auth/
│       └── authentication_db.py     # Database-backed authentication (400+ lines)
├── data/
│   └── users.db                     # SQLite database (created automatically)
├── migrate_users_to_db.py           # Migration script
└── DATABASE_MIGRATION_GUIDE.md      # This file
```

### Modified Files

```
ForexAnalyzer/
├── .gitignore                       # Added database exclusions
├── app.py                           # Updated to use AuthenticatorDB
├── pages/
│   ├── 1_📊_Scanner.py             # Updated to use AuthenticatorDB
│   ├── 2_🤖_Training.py            # Updated to use AuthenticatorDB
│   └── 3_👥_User_Management.py     # Updated to use AuthenticatorDB
└── config/
    └── users.yaml.backup_*          # YAML backup (keep for rollback)
```

---

## 🔐 Security Features

### 1. Password Hashing
```python
# Passwords are hashed with bcrypt
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

### 2. Account Locking
- After **5 failed login attempts**, account is locked for **30 minutes**
- Automatic unlock after lockout period expires
- Failed attempts reset on successful login

### 3. Audit Trail
All actions logged:
- `LOGIN_SUCCESS` - Successful login
- `LOGIN_FAILED` - Failed login attempt
- `USER_CREATED` - New user created
- `USER_UPDATED` - User details updated
- `USER_DELETED` - User deactivated
- `PASSWORD_CHANGED` - Password changed
- `USER_MIGRATED` - Migrated from YAML

### 4. Soft Delete
Users are marked as inactive (`is_active = 0`) instead of being permanently deleted. This preserves audit trail and allows account recovery.

---

## 🛠️ Database Operations

### View All Users
```bash
sqlite3 data/users.db "SELECT * FROM users;"
```

### View Audit Log
```bash
sqlite3 data/users.db "SELECT u.username, a.action, a.details, a.timestamp FROM audit_log a LEFT JOIN users u ON a.user_id = u.id ORDER BY a.timestamp DESC LIMIT 10;"
```

### Unlock Locked Account
```bash
sqlite3 data/users.db "UPDATE users SET locked_until = NULL, failed_login_attempts = 0 WHERE username = 'admin';"
```

### Reset Password Manually
```python
import bcrypt
new_password = "newpassword123"
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(password_hash)
# Then update in database:
# UPDATE users SET password_hash = '<hash>' WHERE username = 'admin';
```

### View Active Sessions
```bash
sqlite3 data/users.db "SELECT u.username, s.session_token, s.created_at, s.expires_at FROM user_sessions s JOIN users u ON s.user_id = u.id;"
```

---

## 🔄 Rollback Instructions

If you need to rollback to YAML-based authentication:

### Step 1: Restore YAML File
```bash
cp config/users.yaml.backup_20251106_174820 config/users.yaml
```

### Step 2: Update Code
In `app.py` and all pages, change:
```python
from src.auth.authentication_db import AuthenticatorDB
st.session_state.auth = AuthenticatorDB()
```

Back to:
```python
from src.auth.authentication import Authenticator
st.session_state.auth = Authenticator()
```

### Step 3: Remove Database (Optional)
```bash
rm data/users.db
```

---

## 📊 Database Maintenance

### Backup Database
```bash
# Create backup
cp data/users.db data/users.db.backup_$(date +%Y%m%d_%H%M%S)

# Or use SQLite backup command
sqlite3 data/users.db ".backup 'data/users.db.backup_$(date +%Y%m%d_%H%M%S)'"
```

### Restore from Backup
```bash
cp data/users.db.backup_20251106_174820 data/users.db
```

### Vacuum Database (Optimize)
```bash
sqlite3 data/users.db "VACUUM;"
```

### Check Database Integrity
```bash
sqlite3 data/users.db "PRAGMA integrity_check;"
```

---

## 🐛 Troubleshooting

### Issue: Cannot login after migration

**Solution 1: Check database exists**
```bash
ls -la data/users.db
```

**Solution 2: Verify users exist**
```bash
sqlite3 data/users.db "SELECT username, name, role, is_active FROM users;"
```

**Solution 3: Check passwords**
If passwords don't work, the migration may have failed. Re-run migration:
```bash
python migrate_users_to_db.py
```

### Issue: Account locked

**Check lock status:**
```bash
sqlite3 data/users.db "SELECT username, failed_login_attempts, locked_until FROM users WHERE username = 'admin';"
```

**Unlock account:**
```bash
sqlite3 data/users.db "UPDATE users SET locked_until = NULL, failed_login_attempts = 0 WHERE username = 'admin';"
```

### Issue: Database file not found

**Create new database with default users:**
```python
python -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); print('Database created with default users')"
```

### Issue: Permission denied on database file

**Fix permissions:**
```bash
chmod 644 data/users.db
```

---

## 🔍 API Reference

### DatabaseManager Class

```python
from src.database.db_manager import DatabaseManager

# Initialize
db = DatabaseManager('data/users.db')

# Create user
success, message = db.create_user(
    username='newuser',
    password='password123',
    name='New User',
    role='user',
    email='newuser@example.com'
)

# Authenticate
success, user_data = db.authenticate_user('newuser', 'password123')

# Get user
user = db.get_user('newuser')

# Get all users
users = db.get_all_users()

# Update user
success, message = db.update_user(
    username='newuser',
    name='Updated Name',
    email='updated@example.com'
)

# Change password
success, message = db.change_password('newuser', 'newpassword123')

# Delete user (soft delete)
success, message = db.delete_user('newuser')

# Get audit log
logs = db.get_audit_log(username='newuser', limit=50)
```

### AuthenticatorDB Class

```python
from src.auth.authentication_db import AuthenticatorDB

# Initialize
auth = AuthenticatorDB('data/users.db')

# Login
success = auth.login('admin', 'admin123')

# Logout
auth.logout()

# Check authentication
is_auth = auth.is_authenticated()

# Get current user
username = auth.get_current_user()
user_id = auth.get_current_user_id()
role = auth.get_current_role()

# Check permissions
can_scan = auth.has_permission(Permissions.SCAN_PAIRS)
is_admin = auth.is_admin()

# Create user (admin only)
success = auth.create_user('newuser', 'password', 'New User', 'user')

# Change password
success = auth.change_password('admin', 'oldpass', 'newpass')

# Delete user (admin only)
success = auth.delete_user('username')

# Get all users (admin only)
users = auth.get_all_users()

# Get audit log (admin only)
logs = auth.get_audit_log(username='admin', limit=100)
```

---

## ✅ Migration Checklist

- [x] Database schema created
- [x] DatabaseManager class implemented
- [x] AuthenticatorDB class implemented
- [x] Migration script created and executed
- [x] YAML backup created
- [x] .gitignore updated to exclude database
- [x] app.py updated to use database authentication
- [x] All pages updated to use database authentication
- [x] Database tested and verified
- [x] Default users created (admin/user)
- [x] Documentation created

---

## 📚 Additional Resources

- **Database Manager**: `src/database/db_manager.py`
- **Authentication**: `src/auth/authentication_db.py`
- **Migration Script**: `migrate_users_to_db.py`
- **Database Location**: `data/users.db`
- **YAML Backup**: `config/users.yaml.backup_*`

---

## 🎉 Summary

✅ **Migration Completed Successfully!**

- Users migrated from YAML to SQLite
- Enhanced security with account locking and audit logging
- All features tested and working
- Backup created for safety
- Application ready to use

### Default Credentials

👤 **Admin Account:**
- Username: `admin`
- Password: `admin123`

👤 **User Account:**
- Username: `user`
- Password: `user123`

---

**Last Updated**: November 6, 2025
**Migration Date**: November 6, 2025 @ 17:48:20
**Status**: ✅ Complete
