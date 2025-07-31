#!/bin/bash
# Secho echo "� Activating virtual environment..."
source ../env/bin/activate

echo "🔧 Setting up production environment..."
# Copy production environment file if it doesn't exist
if [ ! -f .prod ]; then
    if [ -f .env.production ]; then
        cp .env.production .prod
        echo "Created .prod from .env.production"
    else
        echo "Warning: No .env.production file found!"
    fi
fi

echo "📊 Collecting static files (this will fix the CSS loading)..."
python manage.py collectstatic --noinput

echo "🔄 Restarting Django server..."
# Kill existing Django process (if running)
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true

# Start Django server in background
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &ng static files (this will fix the CSS loading)..."
python manage.py collectstatic --noinput

echo "🔄 Restarting Django server..."
# Kill existing Django process (if running)
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true

# Start Django server in background
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &loyment script for VPS
# Run this script ON YOUR VPS after you've pushed changes to GitHub

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /home/rentals/epc_parts_store/epcdata

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo "🔧 Activating virtual environment..."
source ../env/bin/activate

echo "� Collecting static files (this will fix the CSS loading)..."
python manage.py collectstatic --noinput --settings=epcdata.onlinesettings

echo "🔄 Restarting Django server..."
# Kill existing Django process (if running)
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true

# Start Django server in background
nohup python manage.py runserver 0.0.0.0:8000 --settings=epcdata.onlinesettings > django.log 2>&1 &

echo "✅ Deployment complete!"
echo "🌐 Your site should be running at http://80.95.207.42:8000"
echo "📄 Static files should now load correctly"
echo "📄 Check django.log for any errors if needed"
