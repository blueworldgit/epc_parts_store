#!/bin/bash
# VPS Deployment Guide for EPC Parts Store
# Run this script on your VPS after pulling the latest changes

echo "🚀 Starting VPS Deployment..."

# 1. Navigate to your project directory
cd /home/rentals/epc_parts_store/epcdata

# 2. Pull the latest changes from Git
echo "📥 Pulling latest changes..."
git pull origin main

# 3. Create production environment file from template
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.production .env
    echo "✅ Created .env file from template"
    echo "❗ IMPORTANT: Edit .env file with your actual production values!"
    echo "   - Set DEBUG=False"
    echo "   - Set SECRET_KEY to a strong production key"
    echo "   - Configure database credentials"
    echo "   - Add Worldpay credentials when ready"
else
    echo "✅ .env file already exists"
fi

# 4. Activate virtual environment (if you have one)
# source venv/bin/activate  # Uncomment if using virtual environment

# 5. Install/update Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 6. Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --settings=epcdata.onlinesettings

# 7. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=epcdata.onlinesettings

# 8. Test the configuration
echo "🔧 Testing Django configuration..."
python manage.py check --settings=epcdata.onlinesettings

echo "✅ Deployment complete!"
echo ""
echo "🔍 Next steps:"
echo "1. Edit /home/rentals/epc_parts_store/epcdata/.env with your production values"
echo "2. Restart your web server (nginx/apache)"
echo "3. Restart your Django application server (gunicorn/uwsgi)"
echo "4. Test the website at http://80.95.207.42:8000"
echo ""
echo "🌐 Static files should now load correctly!"
