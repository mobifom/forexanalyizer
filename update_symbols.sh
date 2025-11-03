#!/bin/bash

# Script to update all XAUUSD=X and XAGUSD=X references to correct symbols

echo "Updating gold and silver symbols in documentation..."

# Update XAUUSD=X to GC=F
find . -name "*.md" -type f ! -path "./.claude/*" -exec sed -i.bak 's/XAUUSD=X/GC=F/g' {} \;

# Update XAGUSD=X to SI=F
find . -name "*.md" -type f ! -path "./.claude/*" -exec sed -i.bak 's/XAGUSD=X/SI=F/g' {} \;

# Update in Python example files
find . -name "*.py" -type f ! -path "./.claude/*" ! -name "update_symbols.sh" -exec sed -i.bak 's/XAUUSD=X/GC=F/g' {} \;
find . -name "*.py" -type f ! -path "./.claude/*" ! -name "update_symbols.sh" -exec sed -i.bak 's/XAGUSD=X/SI=F/g' {} \;

# Remove backup files
find . -name "*.bak" -type f -delete

echo "Done! All symbols updated to:"
echo "  Gold: GC=F (Gold Futures)"
echo "  Silver: SI=F (Silver Futures)"
