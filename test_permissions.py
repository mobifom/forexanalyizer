#!/usr/bin/env python3
"""
Test script for authentication and permissions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.auth.authentication_db import AuthenticatorDB, Role, Permissions, ROLE_PERMISSIONS

print('=' * 60)
print('AUTHENTICATION SYSTEM TEST')
print('=' * 60)

# Test permissions
print('\nROLE PERMISSIONS:')
print('-' * 60)

for role, perms in ROLE_PERMISSIONS.items():
    print(f'\n{role.upper()}:')
    for perm in perms:
        print(f'  ✓ {perm}')

print('\n' + '=' * 60)
print('PERMISSION CHECKS')
print('=' * 60)

# Test data
admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
user_perms = ROLE_PERMISSIONS[Role.USER]

print('\nADMIN has access to:')
for perm in admin_perms:
    print(f'  ✓ {perm}')

print(f'\nTotal admin permissions: {len(admin_perms)}')

print('\nUSER has access to:')
for perm in user_perms:
    print(f'  ✓ {perm}')

print(f'\nTotal user permissions: {len(user_perms)}')

print('\nUSER does NOT have access to:')
restricted = [p for p in admin_perms if p not in user_perms]
for perm in restricted:
    print(f'  ✗ {perm}')

print('\n' + '=' * 60)
print('UI ELEMENTS HIDDEN FOR REGULAR USERS')
print('=' * 60)
print('\nThe following buttons/features are hidden for regular users:')
for perm in restricted:
    if perm == Permissions.REFRESH_DATA:
        print(f'\n  ✗ "🔄 Refresh Latest Data" button (Main page)')
        print(f'    ✗ "🔄 Refresh All Data" button (Scanner page)')
    elif perm == Permissions.TRAIN_MODEL:
        print(f'\n  ✗ "🤖 Train ML Model" button (Main page)')
        print(f'    ✗ Entire Training page is blocked')
    elif perm == Permissions.MANAGE_USERS:
        print(f'\n  ✗ Entire User Management page is blocked')
    elif perm == Permissions.CHANGE_SETTINGS:
        print(f'\n  ✗ Change Settings permission')

print('\n' + '=' * 60)
print('TEST COMPLETED')
print('=' * 60)
