#!/bin/bash
# Safe fix: Update ONLY Worldpay credentials in .env (keeps current database settings)
# This updates the file that's currently being loaded

echo "🔧 Safely updating Worldpay credentials in current .env file..."

# Navigate to Django project
cd /home/rentals/epc_parts_store/epcdata

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up current .env"

# Update ONLY the Worldpay credentials to live values
echo "🌍 Updating Worldpay credentials to LIVE mode..."

# Update test mode to false
sed -i 's/WORLDPAY_TEST_MODE=True/WORLDPAY_TEST_MODE=False/' .env
sed -i 's/WORLDPAY_TEST_MODE=true/WORLDPAY_TEST_MODE=False/' .env

# Update username to live
sed -i 's/WORLDPAY_USERNAME=evQNpTg2ScurKUxK/WORLDPAY_USERNAME=2UfzfFhGOus54k5G/' .env

# Update password to live
sed -i 's/WORLDPAY_PASSWORD=.*/WORLDPAY_PASSWORD=LNhlWjrSnLAl9NJxOk9FyDk5uOCN6OgdWSEU2nWXcCwoYwOBQhI1eQ9ut5EsbBS7/' .env

# Add missing Gateway URL if not present
if ! grep -q "WORLDPAY_GATEWAY_URL" .env; then
    echo "" >> .env
    echo "# Worldpay Gateway API URL" >> .env
    echo "WORLDPAY_GATEWAY_URL=https://access.worldpay.com/payments/authorizations" >> .env
fi

# Update Gateway URL to live endpoint
sed -i 's|WORLDPAY_GATEWAY_URL=https://try.access.worldpay.com/payments/authorizations|WORLDPAY_GATEWAY_URL=https://access.worldpay.com/payments/authorizations|' .env

echo ""
echo "✅ Updated Worldpay credentials in .env"
echo ""
echo "📋 Current Worldpay settings in .env:"
grep -E "WORLDPAY_" .env
echo ""
echo "🔄 Database settings remain unchanged:"
grep -E "DB_|DATABASE_" .env
echo ""
echo "🚀 Now restart your Django application:"
echo "   pkill -f gunicorn"
echo "   # Then restart your gunicorn process"
echo ""
echo "🧪 Test the fix:"
echo "   curl https://vanparts-direct.co.uk/debug/worldpay-config/"
