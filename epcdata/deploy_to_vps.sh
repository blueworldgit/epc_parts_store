#!/bin/bash
# VPS Deployment Script for Django Static Files Fix
# Run this script on your VPS after pulling the latest changes

echo "🚀 Starting VPS deployment..."

# Navigate to project directory
cd /home/rentals/epc_parts_store/epcdata

# Activate virtual environment
echo "📦 Activating virtual environment..."
source /home/rentals/epc_parts_store/env/bin/activate

# Set the correct Django settings module for production
echo "⚙️ Setting Django settings module..."
export DJANGO_SETTINGS_MODULE=epcdata.onlinesettings

# Copy the production environment file
echo "📋 Setting up environment variables..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.production .env
    echo "⚠️  IMPORTANT: Edit the .env file with your actual values!"
    echo "   - Set DEBUG=False"
    echo "   - Set SECRET_KEY to a secure value"
    echo "   - Set database credentials"
    echo "   - Set Worldpay credentials"
fi

# Install/update requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Collect static files with correct settings
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --settings=epcdata.onlinesettings

# Check if static files were collected correctly
echo "🔍 Checking static files..."
if [ -f "staticfiles/motortemplate/uren/assets/css/vendor/bootstrap.min.css" ]; then
    echo "✅ Bootstrap CSS found in staticfiles!"
else
    echo "❌ Bootstrap CSS not found! Checking source..."
    if [ -f "motortemplate/uren/assets/css/vendor/bootstrap.min.css" ]; then
        echo "✅ Bootstrap CSS found in source directory"
    else
        echo "❌ Bootstrap CSS not found in source directory!"
    fi
fi

# Run Django checks
echo "🧪 Running Django checks..."
python manage.py check --settings=epcdata.onlinesettings

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate --settings=epcdata.onlinesettings

echo "✅ Deployment complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit the .env file with your actual values"
echo "2. Restart your Django server: sudo systemctl restart your-django-service"
echo "3. Test the static files: curl http://80.95.207.42:8000/static/motortemplate/uren/assets/css/vendor/bootstrap.min.css"
echo ""
