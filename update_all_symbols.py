#!/usr/bin/env python3
"""
Update all old gold/silver symbols to new Oanda spot symbols (XAU_USD and XAG_USD)
"""

import os
import glob

# Symbol mappings (update to Oanda spot symbols)
replacements = {
    'XAUUSD=X': 'XAU_USD',
    'XAGUSD=X': 'XAG_USD',
    'GC=F': 'XAU_USD',  # Futures to spot
    'SI=F': 'XAG_USD',  # Futures to spot
}

# Files to update
patterns = ['*.md', '*.py', '*.txt']
exclude_dirs = ['.claude', '__pycache__', 'venv', 'env']

def should_process(filepath):
    """Check if file should be processed"""
    for exclude in exclude_dirs:
        if exclude in filepath:
            return False
    # Don't update this script itself
    if 'update_all_symbols.py' in filepath:
        return False
    return True

files_updated = []

print("Updating gold and silver symbols in all files...")
print("=" * 70)

for pattern in patterns:
    for filepath in glob.glob(f"**/{pattern}", recursive=True):
        if not should_process(filepath):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply replacements
            for old_symbol, new_symbol in replacements.items():
                if old_symbol in content:
                    content = content.replace(old_symbol, new_symbol)
                    print(f"  {filepath}: {old_symbol} → {new_symbol}")

            # Write back if changed
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated.append(filepath)

        except Exception as e:
            print(f"  Error processing {filepath}: {e}")

print("\n" + "=" * 70)
print(f"Updated {len(files_updated)} files")
print("=" * 70)

print("\nSymbol changes:")
print("  XAUUSD=X → XAU_USD (Gold Spot)")
print("  XAGUSD=X → XAG_USD (Silver Spot)")
print("  GC=F → XAU_USD (Gold Futures → Spot)")
print("  SI=F → XAG_USD (Silver Futures → Spot)")

print("\n✓ All documentation and code updated to use Oanda spot symbols!")
