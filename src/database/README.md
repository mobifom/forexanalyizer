# Database Package - User Management

## Overview

This package provides SQLite database management for user authentication and authorization in the Forex Analyzer application.

---

## Components

### 1. DatabaseManager (`db_manager.py`)

The core database management class that handles all database operations.

#### Features:
- ✅ User CRUD operations (Create, Read, Update, Delete)
- ✅ Bcrypt password hashing
- ✅ Account locking after failed login attempts
- ✅ Audit logging for all actions
- ✅ Session tracking
- ✅ Soft delete (users marked inactive)

#### Database Schema:

**users table**
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Bcrypt hashed password
- `name`: Full name
- `email`: Email address (optional)
- `role`: User role (admin/user)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last successful login
- `is_active`: Active status (1=active, 0=inactive)
- `failed_login_attempts`: Counter for failed logins
- `locked_until`: Timestamp until account is locked

**user_sessions table**
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_token`: Unique session token
- `created_at`: Session creation time
- `expires_at`: Session expiration time
- `ip_address`: Client IP address (optional)
- `user_agent`: Client user agent (optional)

**audit_log table**
- `id`: Primary key
- `user_id`: Foreign key to users
- `action`: Action type (LOGIN_SUCCESS, USER_CREATED, etc.)
- `details`: Action details
- `ip_address`: Client IP address (optional)
- `timestamp`: Action timestamp

---

## Usage Examples

### Initialize DatabaseManager

```python
from src.database.db_manager import DatabaseManager

# Create database manager
db = DatabaseManager('data/users.db')
```

### Create User

```python
success, message = db.create_user(
    username='johndoe',
    password='securepassword123',
    name='John Doe',
    role='user',
    email='john@example.com'
)

if success:
    print(f"User created: {message}")
else:
    print(f"Error: {message}")
```

### Authenticate User

```python
success, user_data = db.authenticate_user('johndoe', 'securepassword123')

if success:
    print(f"Welcome {user_data['name']}!")
    print(f"Role: {user_data['role']}")
else:
    print("Invalid credentials")
```

### Get User Information

```python
# Get single user
user = db.get_user('johndoe')
print(f"Name: {user['name']}")
print(f"Email: {user['email']}")
print(f"Last login: {user['last_login']}")

# Get all users
users = db.get_all_users()
for user in users:
    print(f"{user['username']} - {user['role']}")
```

### Update User

```python
success, message = db.update_user(
    username='johndoe',
    name='John Doe Jr.',
    email='johnjr@example.com'
)
```

### Change Password

```python
success, message = db.change_password(
    username='johndoe',
    new_password='newsecurepassword456'
)
```

### Delete User (Soft Delete)

```python
success, message = db.delete_user('johndoe')
# User is marked as inactive, not permanently deleted
```

### View Audit Log

```python
# Get all audit log entries (last 100)
logs = db.get_audit_log(limit=100)

# Get audit log for specific user
logs = db.get_audit_log(username='johndoe', limit=50)

for log in logs:
    print(f"{log['timestamp']}: {log['action']} - {log['details']}")
```

---

## Security Features

### 1. Password Hashing

Passwords are hashed using bcrypt with automatic salt generation:

```python
import bcrypt

# Hash password
password_hash = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt()
).decode('utf-8')

# Verify password
is_valid = bcrypt.checkpw(
    password.encode('utf-8'),
    password_hash.encode('utf-8')
)
```

### 2. Account Locking

After 5 failed login attempts:
- Account is locked for 30 minutes
- `locked_until` timestamp is set
- Further login attempts are rejected until lockout expires

```python
# Account locking logic
if failed_attempts >= 5:
    lock_until = datetime.now() + timedelta(minutes=30)
    # Lock account
```

### 3. Audit Logging

All user actions are logged:

| Action | Description |
|--------|-------------|
| `LOGIN_SUCCESS` | Successful login |
| `LOGIN_FAILED` | Failed login attempt |
| `USER_CREATED` | New user created |
| `USER_UPDATED` | User details updated |
| `USER_DELETED` | User deactivated |
| `PASSWORD_CHANGED` | Password changed |
| `USER_MIGRATED` | User migrated from YAML |

### 4. Soft Delete

Users are never permanently deleted:
- `is_active` flag set to 0
- User data preserved for audit trail
- Can be reactivated if needed

---

## Database Initialization

The database is automatically initialized when DatabaseManager is instantiated:

```python
db = DatabaseManager('data/users.db')
# Creates database file if it doesn't exist
# Creates tables if they don't exist
# Creates indexes for performance
```

Tables and indexes are created with `IF NOT EXISTS` clause, so it's safe to initialize multiple times.

---

## Error Handling

All database operations return tuple `(success: bool, message: str)`:

```python
success, message = db.create_user(...)

if success:
    # Operation succeeded
    print(f"Success: {message}")
else:
    # Operation failed
    print(f"Error: {message}")
    # Handle error appropriately
```

Common errors:
- User already exists (IntegrityError)
- User not found
- Account is locked
- Account is inactive

---

## Performance

### Indexes

Indexes are created for common queries:

```sql
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_session_token ON user_sessions(session_token);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
```

### Connection Management

Each operation opens and closes its own connection:

```python
def _get_connection(self):
    conn = sqlite3.Connection(self.db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn
```

This ensures no connection leaks and thread safety.

---

## Testing

### Manual Testing

```python
# Test database operations
from src.database.db_manager import DatabaseManager

db = DatabaseManager('test_users.db')

# Create user
success, msg = db.create_user('testuser', 'testpass', 'Test User', 'user')
assert success, f"Failed to create user: {msg}"

# Authenticate
success, user = db.authenticate_user('testuser', 'testpass')
assert success, "Authentication failed"
assert user['username'] == 'testuser'

# Get user
user = db.get_user('testuser')
assert user is not None

# Update user
success, msg = db.update_user('testuser', name='Updated Name')
assert success

# Change password
success, msg = db.change_password('testuser', 'newpass')
assert success

# Delete user
success, msg = db.delete_user('testuser')
assert success

print("All tests passed!")
```

### Using SQLite Command Line

```bash
# Open database
sqlite3 data/users.db

# View users
SELECT * FROM users;

# View audit log
SELECT u.username, a.action, a.timestamp
FROM audit_log a
LEFT JOIN users u ON a.user_id = u.id
ORDER BY a.timestamp DESC;

# Check account status
SELECT username, failed_login_attempts, locked_until, is_active
FROM users
WHERE username = 'admin';
```

---

## Migration

To migrate existing users from YAML to database, use the migration script:

```bash
python migrate_users_to_db.py
```

The script:
1. Reads users from `config/users.yaml`
2. Creates database and tables
3. Migrates users (preserves existing password hashes)
4. Creates backup of YAML file
5. Logs migration in audit log

---

## Best Practices

### 1. Always Use DatabaseManager

Don't access the database directly. Use DatabaseManager methods:

```python
# Good
db = DatabaseManager('data/users.db')
user = db.get_user('username')

# Bad
conn = sqlite3.connect('data/users.db')
cursor.execute("SELECT * FROM users WHERE username = ?", ('username',))
```

### 2. Check Return Values

Always check the success flag:

```python
success, message = db.create_user(...)
if not success:
    # Handle error
    log.error(f"Failed to create user: {message}")
    return
```

### 3. Use Audit Logging

The DatabaseManager automatically logs actions. For custom actions, use `_log_action()`:

```python
cursor = conn.cursor()
db._log_action(
    cursor,
    user_id,
    'CUSTOM_ACTION',
    'Action details',
    ip_address='127.0.0.1'
)
```

### 4. Backup Database Regularly

```bash
# Daily backup
cp data/users.db data/backups/users_$(date +%Y%m%d).db

# Or use SQLite backup
sqlite3 data/users.db ".backup 'data/backups/users_$(date +%Y%m%d).db'"
```

### 5. Never Commit Database to Git

The `.gitignore` file already excludes database files:

```gitignore
# SQLite database
data/users.db
data/*.db
*.db
```

---

## Troubleshooting

### Database Locked Error

If you get "database is locked" error:

```python
# Increase timeout
conn = sqlite3.connect('data/users.db', timeout=10.0)
```

### Corrupt Database

Check integrity:

```bash
sqlite3 data/users.db "PRAGMA integrity_check;"
```

If corrupt, restore from backup:

```bash
cp data/backups/users_20251106.db data/users.db
```

### Reset Database

To start fresh:

```bash
# Backup first!
cp data/users.db data/users.db.backup

# Remove database
rm data/users.db

# Restart app - database will be recreated with default users
streamlit run app.py
```

---

## API Reference

### DatabaseManager Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `db_path: str` | None | Initialize database |
| `create_user` | `username, password, name, role, email` | `(bool, str)` | Create new user |
| `authenticate_user` | `username, password` | `(bool, Dict)` | Authenticate user |
| `get_user` | `username` | `Dict or None` | Get user by username |
| `get_all_users` | None | `List[Dict]` | Get all users |
| `update_user` | `username, name, email, role` | `(bool, str)` | Update user details |
| `change_password` | `username, new_password` | `(bool, str)` | Change password |
| `delete_user` | `username` | `(bool, str)` | Soft delete user |
| `get_audit_log` | `username, limit` | `List[Dict]` | Get audit log |

---

## Dependencies

- `sqlite3` (built-in Python module)
- `bcrypt` (for password hashing)
- `datetime` (for timestamps)
- `logging` (for error logging)

Install bcrypt:
```bash
pip install bcrypt
```

---

## License

Part of Forex Analyzer Pro - Internal component

---

**Last Updated**: November 6, 2025
**Version**: 1.0.0
