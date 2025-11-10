# 🔑 Password Management Guide

## Quick Reference

### Reset Admin Password

If you've forgotten the admin password or need to reset it, use the reset script:

```bash
python reset_admin_password.py
```

The script will prompt you to enter a new password (minimum 6 characters).

**Current Admin Credentials:**
- Username: `admin`
- Password: `admin123`

---

## Password Management Options

### Option 1: Using the GUI (Recommended)

1. Login as admin
2. Go to **User Management** page
3. Click **"🔑 Change Password"** tab
4. Enter current password and new password
5. Click "Change Password"

✅ **Advantages:**
- User-friendly interface
- Validates current password
- Automatically logged in audit trail
- No command line required

### Option 2: Using Reset Script

If you cannot login (forgotten password), use the reset script:

```bash
python reset_admin_password.py
```

⚠️ **Note:** This method bypasses current password validation and should only be used for password recovery.

### Option 3: Using Database Directly (Advanced)

For direct database access:

```bash
# Generate password hash in Python
python -c "import bcrypt; password='newpassword123'; hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'); print(hash)"

# Update in database
sqlite3 data/users.db "UPDATE users SET password_hash = '<paste-hash-here>' WHERE username = 'admin';"
```

---

## Default Passwords

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** admin
- **Permissions:** Full access (all features)

### User Account
- **Username:** `user`
- **Password:** `user123`
- **Role:** user
- **Permissions:** Limited (analysis, scanning only)

⚠️ **IMPORTANT:** Change these default passwords after first login!

---

## Password Requirements

- **Minimum Length:** 6 characters (recommended: 12+ for production)
- **Hashing:** Bcrypt with automatic salt generation
- **Storage:** Never stored in plain text
- **Change Frequency:** Recommended every 90 days for production

---

## Account Lockout

After **5 failed login attempts**, accounts are automatically locked for **30 minutes**.

### Unlock Locked Account

**Option 1: Wait 30 minutes** - Account automatically unlocks

**Option 2: Manual unlock** (database access required):

```bash
sqlite3 data/users.db "UPDATE users SET locked_until = NULL, failed_login_attempts = 0 WHERE username = 'admin';"
```

### Check Lock Status

```bash
sqlite3 data/users.db "SELECT username, failed_login_attempts, locked_until FROM users WHERE username = 'admin';"
```

---

## Security Best Practices

### 1. Change Default Passwords Immediately

The default passwords (`admin123` and `user123`) are publicly documented and should be changed immediately in production environments.

### 2. Use Strong Passwords

- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Avoid common words or patterns
- Don't reuse passwords from other services

### 3. Regular Password Changes

- Change passwords every 90 days
- Especially important for admin accounts
- Use password manager to track changes

### 4. Monitor Audit Log

Regularly check the audit log for suspicious activity:

```bash
sqlite3 data/users.db "SELECT u.username, a.action, a.timestamp FROM audit_log a LEFT JOIN users u ON a.user_id = u.id WHERE a.action LIKE '%FAILED%' ORDER BY a.timestamp DESC LIMIT 20;"
```

### 5. Backup Database

Before password changes, backup the database:

```bash
cp data/users.db data/users.db.backup_$(date +%Y%m%d)
```

---

## Troubleshooting

### Problem: Cannot Login After Password Change

**Solution 1: Use reset script**
```bash
python reset_admin_password.py
```

**Solution 2: Check account status**
```bash
sqlite3 data/users.db "SELECT username, is_active, failed_login_attempts, locked_until FROM users WHERE username = 'admin';"
```

**Solution 3: Restore from backup**
```bash
cp data/users.db.backup_20251106 data/users.db
```

### Problem: Account Locked

**Check lock status:**
```bash
sqlite3 data/users.db "SELECT username, locked_until FROM users WHERE username = 'admin';"
```

**Unlock immediately:**
```bash
sqlite3 data/users.db "UPDATE users SET locked_until = NULL, failed_login_attempts = 0 WHERE username = 'admin';"
```

### Problem: Forgot Which Account is Admin

**List all users with roles:**
```bash
sqlite3 data/users.db "SELECT username, name, role, is_active FROM users ORDER BY role;"
```

---

## Creating New Users

### Via GUI (Recommended)

1. Login as admin
2. Go to **User Management** page
3. Click **"➕ Create User"** tab
4. Fill in user details
5. Click "Create User"

### Via Python Script

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager('data/users.db')

success, message = db.create_user(
    username='newuser',
    password='securepassword123',
    name='New User',
    role='user',  # or 'admin'
    email='newuser@example.com'
)

print(message)
```

---

## Changing User Passwords (Admin Only)

Admins can change any user's password through the GUI:

1. Login as admin
2. Go to **User Management** page
3. Click **"🔑 Change Password"** tab
4. Select target user
5. Enter new password (admin password not required)
6. Click "Change Password"

---

## Audit Trail

All password-related actions are logged in the `audit_log` table:

### View Password Changes

```bash
sqlite3 data/users.db "SELECT u.username, a.action, a.details, a.timestamp FROM audit_log a LEFT JOIN users u ON a.user_id = u.id WHERE a.action = 'PASSWORD_CHANGED' ORDER BY a.timestamp DESC;"
```

### View Failed Login Attempts

```bash
sqlite3 data/users.db "SELECT u.username, a.action, a.details, a.timestamp FROM audit_log a LEFT JOIN users u ON a.user_id = u.id WHERE a.action = 'LOGIN_FAILED' ORDER BY a.timestamp DESC LIMIT 20;"
```

### View All User Actions

```bash
sqlite3 data/users.db "SELECT u.username, a.action, a.timestamp FROM audit_log a LEFT JOIN users u ON a.user_id = u.id WHERE u.username = 'admin' ORDER BY a.timestamp DESC LIMIT 50;"
```

---

## Emergency Access

If you've completely locked yourself out:

### Method 1: Reset Database (Nuclear Option)

```bash
# Backup first!
mv data/users.db data/users.db.locked

# Restart app - will create fresh database with defaults
streamlit run app.py
```

### Method 2: Create New Admin

```bash
python -c "
from src.database.db_manager import DatabaseManager
db = DatabaseManager('data/users.db')
db.create_user('recovery', 'recovery123', 'Recovery Admin', 'admin')
print('Created recovery admin: recovery/recovery123')
"
```

---

## Password Reset Script Usage

### Interactive Mode

```bash
python reset_admin_password.py
```

Then enter new password when prompted.

### Scripted Mode (for automation)

```bash
echo -e "newpassword\nnewpassword" | python reset_admin_password.py
```

⚠️ **Warning:** Only use scripted mode in secure environments as it may expose passwords in process list.

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| Reset admin password | `python reset_admin_password.py` |
| View all users | `sqlite3 data/users.db "SELECT username, role FROM users;"` |
| Unlock account | `sqlite3 data/users.db "UPDATE users SET locked_until=NULL, failed_login_attempts=0 WHERE username='admin';"` |
| View failed logins | `sqlite3 data/users.db "SELECT * FROM audit_log WHERE action='LOGIN_FAILED' ORDER BY timestamp DESC LIMIT 10;"` |
| Backup database | `cp data/users.db data/users.db.backup_$(date +%Y%m%d)` |
| Check lock status | `sqlite3 data/users.db "SELECT username, locked_until FROM users;"` |

---

## Support

For more information, see:
- **DATABASE_MIGRATION_GUIDE.md** - Complete database documentation
- **src/database/README.md** - Database API reference
- **User Management Page** - GUI-based user management (admin only)

---

**Last Updated:** November 7, 2025
**Status:** Admin password reset to `admin123`
