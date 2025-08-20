#!/bin/bash
# Quick fix for production server - Update to live Worldpay configuration
# Run this on your Linux server

echo "🚀 Updating server to LIVE Worldpay configuration..."

# Create backup
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up .env.production"

# Update the existing variables to live configuration
echo "🔧 Updating Worldpay configuration to LIVE mode..."

# Update to live mode
sed -i 's/WORLDPAY_TEST_MODE=true/WORLDPAY_TEST_MODE=False/' .env.production

# Update to live endpoint
sed -i 's|WORLDPAY_GATEWAY_URL=https://try.access.worldpay.com/payments/authorizations|WORLDPAY_GATEWAY_URL=https://access.worldpay.com/payments/authorizations|' .env.production

# Update to live credentials (you need to replace these with your actual live credentials)
sed -i 's/WORLDPAY_USERNAME=evQNpTg2ScurKUxK/WORLDPAY_USERNAME=2UfzfFhGOus54k5G/' .env.production
# You need to update the password manually with your live password
echo "⚠️  CRITICAL: You must update WORLDPAY_PASSWORD with your live password!"

echo ""
echo "📋 Current Worldpay configuration:"
grep -E "WORLDPAY_|GATEWAY_" .env.production

echo ""
echo "🔧 Manual steps required:"
echo "1. Update WORLDPAY_PASSWORD with your live password:"
echo "   sed -i 's/WORLDPAY_PASSWORD=.*/WORLDPAY_PASSWORD=YOUR_LIVE_PASSWORD/' .env.production"
echo ""
echo "2. Restart your Django application:"
echo "   sudo systemctl restart your-django-service"
echo "   # OR"
echo "   sudo supervisorctl restart your-django-app"
echo ""
echo "3. Test the configuration:"
echo "   curl https://yourserver.com/debug/worldpay-config/"
