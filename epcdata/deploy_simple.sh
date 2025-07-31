#!/bin/bash
# Simple deployment script for VPS
# Run this script ON YOUR VPS after you've pushed changes to GitHub

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /home/rentals/epc_parts_store/epcdata

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo "🔧 Activating virtual environment..."
source ../env/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

echo "🗃️ Running database migrations..."
python manage.py migrate --settings=epcdata.onlinesettings

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=epcdata.onlinesettings

echo "🔄 Restarting Django server..."
# Kill existing Django process
pkill -f "python.*manage.py.*runserver"

# Start Django server in background
nohup python manage.py runserver 0.0.0.0:8000 --settings=epcdata.onlinesettings > django.log 2>&1 &

echo "✅ Deployment complete!"
echo "🌐 Your site should be running at http://80.95.207.42:8000"
echo "📄 Check django.log for any errors"
