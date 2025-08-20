#!/bin/bash
# Server Environment Update Script
# Run this on your server to update the production environment

echo "🚀 Updating Production Environment for Worldpay Gateway API"
echo "================================================================"

# Navigate to the project directory
cd /path/to/your/epc_parts_store/epcdata

# Check if production environment file exists
if [ -f ".env.production" ]; then
    echo "✅ Found .env.production file"
    
    # Backup the current production environment
    cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
    echo "📦 Backed up current .env.production"
    
    # Show current Worldpay config
    echo "🔍 Current Worldpay configuration:"
    grep -E "WORLDPAY_|WORLDPAY_" .env.production || echo "No Worldpay config found"
    
else
    echo "❌ .env.production file not found!"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

echo ""
echo "🔧 Manual Steps Required:"
echo "1. Edit .env.production and update Worldpay configuration:"
echo "   WORLDPAY_USERNAME=2UfzfFhGOus54k5G"
echo "   WORLDPAY_PASSWORD=LNhlWjrSnLAl9NJxOk9FyDk5uOCN6OgdWSEU2nWXcCwoYwOBQhI1eQ9ut5EsbBS7"
echo "   WORLDPAY_ENTITY_ID=PO4080334630"
echo "   WORLDPAY_TEST_MODE=False"
echo ""
echo "2. Restart your Django application"
echo "3. Test payment processing"

echo ""
echo "📋 Verification Commands:"
echo "python manage.py shell -c \"from django.conf import settings; print('Worldpay Username:', getattr(settings, 'WORLDPAY_USERNAME', 'NOT SET'))\""
echo "python manage.py shell -c \"from django.conf import settings; print('Test Mode:', getattr(settings, 'WORLDPAY_TEST_MODE', 'NOT SET'))\""
