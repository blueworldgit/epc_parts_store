#!/bin/bash
# Complete fix: Replace ALL Worldpay credentials in .env file
# This will ensure all old credentials are replaced with live ones

echo "🔧 Completely updating ALL Worldpay credentials in .env file..."

# Navigate to Django project
cd /home/rentals/epc_parts_store/epcdata

# Backup current .env
cp .env .env.backup.complete.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up current .env"

echo "📋 Current .env content (before fix):"
echo "======================================"
cat .env
echo "======================================"
echo ""

echo "🌍 Replacing ALL Worldpay credentials..."

# Remove ALL existing Worldpay lines first
sed -i '/WORLDPAY_/d' .env

# Add the complete live Worldpay configuration at the end
cat >> .env << 'EOF'

# Worldpay Gateway API - Live Configuration (Updated Aug 20, 2025)
WORLDPAY_USERNAME=2UfzfFhGOus54k5G
WORLDPAY_PASSWORD=LNhlWjrSnLAl9NJxOk9FyDk5uOCN6OgdWSEU2nWXcCwoYwOBQhI1eQ9ut5EsbBS7
WORLDPAY_ENTITY_ID=PO4080334630
WORLDPAY_TEST_MODE=False
WORLDPAY_GATEWAY_URL=https://access.worldpay.com/payments/authorizations
EOF

echo "✅ Replaced ALL Worldpay credentials in .env"
echo ""
echo "📋 Updated .env content (after fix):"
echo "======================================"
cat .env
echo "======================================"
echo ""
echo "🔍 Worldpay lines only:"
grep -E "WORLDPAY_" .env
echo ""
echo "🚀 Now restart Django to load new credentials:"
echo "   sudo systemctl restart epcdata.service"
echo ""
echo "🧪 Then test the fix:"
echo "   curl https://vanparts-direct.co.uk/debug/worldpay-config/"
