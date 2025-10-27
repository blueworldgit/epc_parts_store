#!/bin/bash
# Complete setup script for vanparts-direct.co.uk production deployment
# Based on server diagnostic from Oct 27, 2025
# Run this as user 'maxis' on server 80.95.207.45

set -e

echo "🚀 VANPARTS-DIRECT.CO.UK PRODUCTION SETUP"
echo "========================================="
echo "Server: $(hostname) ($(hostname -I | awk '{print $1}'))"
echo "User: $(whoami)"
echo "Date: $(date)"
echo ""

# Configuration variables
PROJECT_DIR="/home/maxis/epc_parts_store/epcdata"
SERVICE_NAME="vanparts-direct"
DOMAIN="vanparts-direct.co.uk"
NGINX_SITE_CONFIG="nginx_vanparts_direct_final.conf"

# Check if we're in the right place
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

echo "✅ Project directory found: $PROJECT_DIR"
cd "$PROJECT_DIR"

# 1. Install required system packages
echo ""
echo "📦 Installing system packages..."
sudo apt update
sudo apt install -y nginx postgresql-client python3-pip python3-venv git certbot python3-certbot-nginx ufw

# 2. Create missing directories and files
echo ""
echo "📁 Setting up directories and missing files..."
mkdir -p media/images logs
chmod 755 media media/images

# Create the missing CSS file
cat > media/header-styles-parent-fixed.css << 'EOF'
/* Header styles for vanparts-direct.co.uk */
/* Auto-generated placeholder - replace with your actual styles */

.header-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 15px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header-logo {
    font-size: 28px;
    font-weight: bold;
    text-decoration: none;
    color: white;
}

.header-nav {
    margin-top: 10px;
}

.header-nav a {
    margin-right: 25px;
    text-decoration: none;
    color: #e8f4f8;
    font-weight: 500;
    transition: color 0.3s ease;
}

.header-nav a:hover {
    color: #ffffff;
    text-decoration: underline;
}

.breadcrumb-container {
    background: #f8f9fa;
    padding: 20px 0;
    border-bottom: 1px solid #dee2e6;
}

/* Add your actual header styles here */
EOF

# Create placeholder breadcrumb image
if command -v convert >/dev/null 2>&1; then
    convert -size 1200x300 gradient:#2a5298-#1e3c72 \
            -fill white -pointsize 48 -gravity center \
            -annotate +0+0 "VAN PARTS DIRECT\nProfessional Motor Parts" \
            media/images/breadcrumb-van-interior.jpg
    echo "✅ Created breadcrumb image with ImageMagick"
else
    # Create a simple colored rectangle with text (requires no external tools)
    cat > media/images/breadcrumb-van-interior.jpg << 'EOF'
<!DOCTYPE html><html><body style="margin:0;background:linear-gradient(45deg,#2a5298,#1e3c72);color:white;font-family:Arial;display:flex;align-items:center;justify-content:center;height:300px;width:1200px;font-size:36px;font-weight:bold;">VAN PARTS DIRECT<br><small style="font-size:24px;">Professional Motor Parts</small></body></html>
EOF
    echo "✅ Created HTML placeholder (install ImageMagick for proper image)"
fi

# Set proper permissions
chown -R maxis:maxis media/
chmod -R 644 media/
chmod 755 media/ media/images/

echo "✅ Created missing media files"

# 3. Virtual environment setup (if needed)
if [ ! -d "env" ]; then
    echo ""
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv env
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install/update packages
echo ""
echo "📚 Installing Python packages..."
source env/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt || pip install django django-oscar psycopg2-binary gunicorn whitenoise python-dotenv djangorestframework sorl-thumbnail django-countries

# 4. Django setup
echo ""
echo "⚙️ Django configuration..."
export DJANGO_ENV=production

# Collect static files
python manage.py collectstatic --noinput
echo "✅ Static files collected"

# Run migrations
python manage.py migrate
echo "✅ Database migrations completed"

# 5. Create systemd service
echo ""
echo "🔧 Setting up systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=vanparts-direct Django Application
After=network.target
Wants=network.target

[Service]
Type=exec
User=maxis
Group=maxis
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_ENV=production
Environment=PATH=$PROJECT_DIR/env/bin
ExecStart=$PROJECT_DIR/env/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 30 epcdata.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR/media
ReadWritePaths=$PROJECT_DIR/logs

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
echo "✅ Systemd service configured"

# 6. Setup Nginx
echo ""
echo "🌐 Setting up Nginx..."

# Copy our nginx configuration
if [ -f "../$NGINX_SITE_CONFIG" ]; then
    sudo cp "../$NGINX_SITE_CONFIG" "/etc/nginx/sites-available/$DOMAIN"
else
    echo "❌ Nginx config file not found: $NGINX_SITE_CONFIG"
    echo "Please ensure the file exists in the project root"
    exit 1
fi

# Enable the site
sudo ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
echo "✅ Nginx configuration valid"

# 7. Setup firewall
echo ""
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
echo "✅ Firewall configured"

# 8. Get SSL certificate
echo ""
echo "🔒 Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d maxusparts.co.uk -d www.maxusparts.co.uk \
    --non-interactive --agree-tos --email sales@vanpartsdirect4u.co.uk
echo "✅ SSL certificate obtained"

# 9. Start services
echo ""
echo "🚀 Starting services..."
sudo systemctl start $SERVICE_NAME
sudo systemctl reload nginx

# 10. Status check
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🔍 Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l
echo ""

echo "🌐 Your site should now be available at:"
echo "   https://vanparts-direct.co.uk"
echo "   https://www.vanparts-direct.co.uk"
echo "   https://maxusparts.co.uk"
echo "   https://www.maxusparts.co.uk"
echo ""

echo "🔧 Useful commands:"
echo "   Restart Django: sudo systemctl restart $SERVICE_NAME"
echo "   View Django logs: sudo journalctl -u $SERVICE_NAME -f"
echo "   Restart Nginx: sudo systemctl restart nginx"
echo "   View Nginx logs: sudo tail -f /var/log/nginx/vanparts-direct.*.log"
echo "   Django admin: https://vanparts-direct.co.uk/admin/"
echo ""

echo "📝 Next steps:"
echo "1. Test the website thoroughly"
echo "2. Create a Django superuser if needed: python manage.py createsuperuser"
echo "3. Import your product data: python import_to_oscar.py"
echo "4. Set up automated backups"
echo "5. Monitor logs for any issues"
echo ""

# Test the deployment
echo "🧪 Testing deployment..."
sleep 5
curl -I https://$DOMAIN || echo "⚠️ HTTPS test failed - may need DNS propagation time"
curl -I http://$DOMAIN || echo "⚠️ HTTP test failed"

echo ""
echo "🎉 Setup complete! Check the URLs above to verify everything is working."