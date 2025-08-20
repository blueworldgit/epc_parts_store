#!/bin/bash
# Update production environment with new Worldpay Gateway API configuration
# Run this script on your Linux server

echo "🚀 Updating production environment for Worldpay Gateway API..."

# Backup current production environment
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up current .env.production"

# Update the production environment file
cat > .env.production << 'EOF'
# Production Environment - Worldpay Gateway API Configuration
# Updated: August 20, 2025

# Django Settings
DEBUG=False
DJANGO_ENV=production

# Database Configuration
DATABASE_NAME=vansdirect
DATABASE_USER=vansdirect
DATABASE_PASSWORD=your_production_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Security
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Worldpay Gateway API - LIVE CONFIGURATION
WORLDPAY_TEST_MODE=False
WORLDPAY_GATEWAY_USERNAME=2UfzfFhGOus54k5G
WORLDPAY_GATEWAY_PASSWORD=your_live_password_here
WORLDPAY_GATEWAY_ENTITY_ID=PO4080334630
WORLDPAY_GATEWAY_URL=https://access.worldpay.com/payments/authorizations

# Static/Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/var/www/your-site/static/
MEDIA_ROOT=/var/www/your-site/media/

# Email Configuration (if used)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your_smtp_host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@domain.com
EMAIL_HOST_PASSWORD=your_email_password

# Cache Configuration (if using Redis/Memcached)
# CACHE_URL=redis://localhost:6379/1

# Logging
LOG_LEVEL=INFO
EOF

echo "✅ Updated .env.production with new Worldpay Gateway API configuration"
echo ""
echo "⚠️  IMPORTANT: You need to update these values manually:"
echo "   - DATABASE_PASSWORD: Your actual production database password"
echo "   - SECRET_KEY: Your actual Django secret key"
echo "   - ALLOWED_HOSTS: Your actual domain names"
echo "   - WORLDPAY_GATEWAY_PASSWORD: Your actual live Worldpay password"
echo "   - Email settings (if using email)"
echo "   - Static/Media paths (adjust for your server setup)"
echo ""
echo "🔧 Quick commands to update the critical values:"
echo "   sed -i 's/your_production_db_password/ACTUAL_PASSWORD/' .env.production"
echo "   sed -i 's/your_production_secret_key/ACTUAL_SECRET/' .env.production"
echo "   sed -i 's/your-domain.com/yourdomain.com/' .env.production"
echo "   sed -i 's/your_live_password_here/ACTUAL_WORLDPAY_PASSWORD/' .env.production"
echo ""
echo "📝 After updating, restart your Django application:"
echo "   sudo systemctl restart your-django-service"
echo "   # OR"
echo "   sudo supervisorctl restart your-django-app"
echo "   # OR restart your WSGI server (gunicorn, uwsgi, etc.)"
