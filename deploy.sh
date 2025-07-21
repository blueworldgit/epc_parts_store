#!/bin/bash
# Quick deployment script for EPC Django Oscar Site

echo "Starting EPC Django Oscar deployment..."

# Set variables
PROJECT_DIR="/var/www/epcdjangosite"
VENV_DIR="$PROJECT_DIR/env"
APP_DIR="$PROJECT_DIR/epcdata"

# Activate virtual environment
source $VENV_DIR/bin/activate

# Navigate to project directory
cd $APP_DIR

# Pull latest code (if using git)
# git pull origin main

# Install/update dependencies
pip install -r requirements_production.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Copy Oscar images if needed
cp $VENV_DIR/lib/python*/site-packages/oscar/static/oscar/img/image_not_found.jpg media/oscar/img/ 2>/dev/null || true
cp $VENV_DIR/lib/python*/site-packages/oscar/static/oscar/img/image_not_found.jpg media/ 2>/dev/null || true

# Set permissions
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 775 $APP_DIR/media

# Restart services
sudo supervisorctl restart epcdjangosite
sudo systemctl reload nginx

echo "Deployment completed successfully!"
echo "Visit your site at: http://your-domain.com"
echo "Admin panel: http://your-domain.com/admin/"
echo "Oscar dashboard: http://your-domain.com/dashboard/"
