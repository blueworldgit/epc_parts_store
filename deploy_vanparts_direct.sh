#!/bin/bash
# Production deployment script for vanparts-direct.co.uk
# Run this on your VPS server (80.95.207.45)

set -e  # Exit on any error

echo "🚀 Starting vanparts-direct.co.uk production deployment..."

# Variables
PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"
NGINX_SITE="vanparts-direct.co.uk"
SERVICE_NAME="vanparts-direct"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Run as maxis user."
   exit 1
fi

# 1. Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install required packages
echo "📦 Installing required packages..."
sudo apt install -y nginx postgresql-client python3-pip python3-venv git certbot python3-certbot-nginx

# 3. Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_DIR/env" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd $PROJECT_DIR
    python3 -m venv env
fi

# 4. Activate virtual environment and install requirements
echo "📚 Installing Python requirements..."
cd $PROJECT_DIR
source env/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt

# 5. Collect static files
echo "📁 Collecting static files..."
export DJANGO_ENV=production
python manage.py collectstatic --noinput

# 6. Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# 7. Create superuser if needed (interactive)
echo "👤 Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one:')
    exit()
else:
    print('Superuser already exists.')
" || python manage.py createsuperuser

# 8. Set up log directories
echo "📝 Setting up log directories..."
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/run/gunicorn
sudo chown maxis:maxis /var/log/gunicorn
sudo chown maxis:maxis /var/run/gunicorn

# 9. Install systemd service
echo "⚙️ Installing systemd service..."
sudo cp /home/maxis/epc_parts_store/vanparts-direct.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# 10. Install Nginx configuration
echo "🌐 Installing Nginx configuration..."
sudo cp /home/maxis/epc_parts_store/nginx_vanparts_direct.conf /etc/nginx/sites-available/$NGINX_SITE
sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site

# 11. Test Nginx configuration
echo "🔧 Testing Nginx configuration..."
sudo nginx -t

# 12. Get SSL certificate with Let's Encrypt
echo "🔒 Setting up SSL certificate..."
sudo certbot --nginx -d vanparts-direct.co.uk -d www.vanparts-direct.co.uk --non-interactive --agree-tos --email sales@vanpartsdirect4u.co.uk

# 13. Start services
echo "🔄 Starting services..."
sudo systemctl start $SERVICE_NAME
sudo systemctl reload nginx

# 14. Check service status
echo "✅ Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager
sudo systemctl status nginx --no-pager

# 15. Test the deployment
echo "🧪 Testing deployment..."
curl -I http://vanparts-direct.co.uk || echo "⚠️ HTTP test failed"
curl -I https://vanparts-direct.co.uk || echo "⚠️ HTTPS test failed"

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Post-deployment checklist:"
echo "   ✅ Service running: sudo systemctl status $SERVICE_NAME"
echo "   ✅ Nginx running: sudo systemctl status nginx"
echo "   ✅ SSL certificate: sudo certbot certificates"
echo "   ✅ Check logs: sudo journalctl -u $SERVICE_NAME -f"
echo "   ✅ Admin panel: https://vanparts-direct.co.uk/admin/"
echo "   ✅ Site health: https://vanparts-direct.co.uk/"
echo ""
echo "🔧 Useful commands:"
echo "   Restart app: sudo systemctl restart $SERVICE_NAME"
echo "   View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "   Update code: cd $PROJECT_DIR && git pull && sudo systemctl restart $SERVICE_NAME"
echo ""