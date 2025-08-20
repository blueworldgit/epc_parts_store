#!/bin/bash
# Complete fix for production server - Update to live Worldpay configuration
# This script will automatically update ALL Worldpay settings to live mode
# Run this on your Linux server, then DELETE this file for security

echo "🚀 Updating server to LIVE Worldpay configuration..."

# Create backup
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up .env.production"

# Update all Worldpay configuration to live mode
echo "🔧 Updating Worldpay configuration to LIVE mode..."

# Update to live mode
sed -i 's/WORLDPAY_TEST_MODE=true/WORLDPAY_TEST_MODE=False/' .env.production
sed -i 's/WORLDPAY_TEST_MODE=True/WORLDPAY_TEST_MODE=False/' .env.production

# Update to live endpoint
sed -i 's|WORLDPAY_GATEWAY_URL=https://try.access.worldpay.com/payments/authorizations|WORLDPAY_GATEWAY_URL=https://access.worldpay.com/payments/authorizations|' .env.production

# Update to live credentials
sed -i 's/WORLDPAY_USERNAME=evQNpTg2ScurKUxK/WORLDPAY_USERNAME=2UfzfFhGOus54k5G/' .env.production
sed -i 's/WORLDPAY_USERNAME=.*/WORLDPAY_USERNAME=2UfzfFhGOus54k5G/' .env.production

# Update password to live password
sed -i 's/WORLDPAY_PASSWORD=.*/WORLDPAY_PASSWORD=LNhlWjrSnLAl9NJxOk9FyDk5uOCN6OgdWSEU2nWXcCwoYwOBQhI1eQ9ut5EsbBS7/' .env.production

# Ensure entity ID is correct
sed -i 's/WORLDPAY_ENTITY_ID=.*/WORLDPAY_ENTITY_ID=PO4080334630/' .env.production

echo ""
echo "✅ Updated configuration complete!"
echo ""
echo "📋 Current Worldpay configuration:"
grep -E "WORLDPAY_" .env.production
echo ""
echo "🔄 Now restart your Django application:"
echo "   sudo systemctl restart your-django-service"
echo "   # OR"
echo "   sudo supervisorctl restart your-django-app"
echo ""
echo "🧪 Test the configuration:"
echo "   curl https://yourserver.com/debug/worldpay-config/"
echo ""
echo "🔒 SECURITY: DELETE this script after use!"
echo "   rm fix_server_worldpay.sh"
