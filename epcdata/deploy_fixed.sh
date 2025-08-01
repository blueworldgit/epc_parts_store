#!/bin/bash

# VPS Deployment Script for EPC Parts Store
# This script handles proper environment setup and database migration

PROJECT_NAME="epc_parts_store"
PROJECT_PATH="/home/rentals/$PROJECT_NAME"
VENV_PATH="$PROJECT_PATH/env"
APP_PATH="$PROJECT_PATH/epcdata"

echo "🚀 Starting VPS deployment for EPC Parts Store..."

# Ensure we're in the correct directory
cd $APP_PATH || { echo "❌ Failed to enter project directory"; exit 1; }

echo "📁 Current directory: $(pwd)"
echo "📋 Files in directory:"
ls -la

# Check environment files
echo ""
echo "🔍 Checking environment files..."
if [[ -f ".env" ]]; then
    echo "✅ Found .env file"
    echo "📝 Database config from .env:"
    grep "DB_" .env | head -5
else
    echo "❌ No .env file found!"
    
    # Check if .env.production exists and copy it
    if [[ -f ".env.production" ]]; then
        echo "📋 Copying .env.production to .env..."
        cp .env.production .env
        echo "✅ Created .env from .env.production"
    else
        echo "❌ No environment file found! Creating basic .env..."
        cat > .env << EOF
SECRET_KEY=django-insecure-aiqpmaxs^h@-@r#-nvtu)%p73-0#h3jkb_q99zj6+znx%+#s@6
DEBUG=False
ALLOWED_HOSTS=80.95.207.42,vanparts-direct.co.uk,www.vanparts-direct.co.uk
DB_ENGINE=django.db.backends.postgresql
DB_NAME=parts_store
DB_USER=postgres
DB_PASSWORD=N0rwich!
DB_HOST=localhost
DB_PORT=5432
EOF
        echo "✅ Created basic .env file"
    fi
fi

# Activate virtual environment
echo ""
echo "🐍 Activating virtual environment..."
source $VENV_PATH/bin/activate || { echo "❌ Failed to activate virtual environment"; exit 1; }
echo "✅ Virtual environment activated"

# Test database connection
echo ""
echo "🔌 Testing database connection..."
python -c "
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        database=os.getenv('DB_NAME', 'parts_store'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection test failed. Check your credentials!"
    exit 1
fi

# Install/update requirements
echo ""
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Run migrations
echo ""
echo "🔄 Running database migrations..."
python manage.py makemigrations --verbosity=2
python manage.py migrate --verbosity=2

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --verbosity=2

# Create superuser if needed
echo ""
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('✅ Superuser already exists')
"

# Test Django
echo ""
echo "🧪 Testing Django configuration..."
python manage.py check --verbosity=2

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start your web server (nginx/apache)"
echo "2. Start your WSGI server (gunicorn/uwsgi)"
echo "3. Visit your site at: http://80.95.207.42"
echo ""
echo "🔐 Admin access:"
echo "   URL: http://80.95.207.42/admin/"
echo "   User: admin"
echo "   Pass: admin123"
