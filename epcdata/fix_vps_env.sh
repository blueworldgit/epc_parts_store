#!/bin/bash

# Quick fix for database credentials on VPS
echo "🔧 Quick fixing database credentials..."

cd /home/rentals/epc_parts_store/epcdata

# Backup existing .env if it exists
if [[ -f ".env" ]]; then
    cp .env .env.backup
    echo "📋 Backed up existing .env to .env.backup"
fi

# Create correct .env file
cat > .env << 'EOF'
# Django settings
SECRET_KEY=django-insecure-aiqpmaxs^h@-@r#-nvtu)%p73-0#h3jkb_q99zj6+znx%+#s@6
DEBUG=False

# Allowed Hosts
ALLOWED_HOSTS=80.95.207.42,vanparts-direct.co.uk,www.vanparts-direct.co.uk,localhost,127.0.0.1,[::1]

# Database settings - VPS Production
DB_ENGINE=django.db.backends.postgresql
DB_NAME=parts_store
DB_USER=postgres
DB_PASSWORD=N0rwich!
DB_HOST=localhost
DB_PORT=5432

# Worldpay Configuration
WORLDPAY_INSTALLATION_ID=YOUR_INSTALLATION_ID_HERE
WORLDPAY_SECRET_KEY=YOUR_SECRET_KEY_HERE
WORLDPAY_CALLBACK_PASSWORD=YOUR_CALLBACK_PASSWORD_HERE
EOF

echo "✅ Created correct .env file with VPS database credentials"
echo ""
echo "📝 Database configuration:"
echo "   Database: parts_store"
echo "   User: postgres"
echo "   Password: N0rwich!"
echo ""
echo "🔄 Now try running your migrations again:"
echo "   source /home/rentals/epc_parts_store/env/bin/activate"
echo "   cd /home/rentals/epc_parts_store/epcdata"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
