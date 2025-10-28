#!/bin/bash

# PostgreSQL Database Recreation Script
# This will completely delete and recreate the database

echo "=== PostgreSQL Database Recreation ==="
echo "WARNING: This will DELETE ALL DATA in the database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Get database connection details from Django settings
cd /home/maxis/epc_parts_store
source env/bin/activate

echo "Getting database details from Django settings..."
python -c "
from django.conf import settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
settings.configure()
from django.conf import settings
db = settings.DATABASES['default']
print(f'DB_NAME={db[\"NAME\"]}')
print(f'DB_USER={db[\"USER\"]}')
print(f'DB_HOST={db[\"HOST\"]}')
print(f'DB_PORT={db[\"PORT\"]}')
" > /tmp/db_config.sh

# Source the config
source /tmp/db_config.sh

echo "Database: $DB_NAME"
echo "Host: $DB_HOST"
echo "User: $DB_USER"

echo "=== Step 1: Dropping existing database ==="
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"

echo "=== Step 2: Creating new database ==="
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER $DB_USER;"

echo "=== Step 3: Running Django migrations ==="
cd /home/maxis/epc_parts_store
source env/bin/activate
python manage.py migrate

echo "=== Step 4: Creating superuser (optional) ==="
echo "Would you like to create a new superuser? (y/n)"
read create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

echo "=== Step 5: Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Step 6: Restarting services ==="
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "=== Database Recreation Complete! ==="
echo "Your database has been completely recreated."
echo "All previous data has been deleted."
echo "You can now access your site with a fresh database."

# Cleanup
rm /tmp/db_config.sh