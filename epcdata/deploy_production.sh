#!/bin/bash
# Production deployment script for EPC Store

echo "Starting production deployment..."

# Activate virtual environment (adjust path as needed)
source env/bin/activate  # For Linux/Mac
# For Windows: env\Scripts\activate

echo "Installing/updating requirements..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py migrate

echo "Creating superuser (if needed)..."
# python manage.py createsuperuser

echo "Starting production server..."
# For production, use gunicorn or similar
# gunicorn epcdata.wsgi:application --bind 0.0.0.0:8000

echo "Deployment complete!"
echo "Static files are in: staticfiles/"
echo "Make sure your web server is configured to serve static files from this directory."
