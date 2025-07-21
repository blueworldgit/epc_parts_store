# EPC Django Oscar E-commerce Site
# Production Deployment Guide

## Server Requirements
- Python 3.8+
- PostgreSQL 12+
- Ubuntu 20.04+ or similar Linux distribution
- 2GB+ RAM
- 20GB+ storage

## Installation Steps

### 1. Prepare Server Environment
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and system dependencies
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx supervisor -y

# Install system packages for image processing
sudo apt install libjpeg-dev libpng-dev libtiff-dev libfreetype6-dev -y
```

### 2. Setup Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE epcdjangosite;
CREATE USER epcuser WITH PASSWORD 'your_strong_password_here';
ALTER ROLE epcuser SET client_encoding TO 'utf8';
ALTER ROLE epcuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE epcuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE epcdjangosite TO epcuser;
\q
```

### 3. Deploy Application
```bash
# Create application directory
sudo mkdir -p /var/www/epcdjangosite
cd /var/www/epcdjangosite

# Clone or upload your code
# (Upload your cleaned project files here)

# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements_production.txt
```

### 4. Configure Environment Variables
Create `/var/www/epcdjangosite/.env`:
```env
DEBUG=False
SECRET_KEY=your_django_secret_key_here
DATABASE_URL=postgres://epcuser:your_strong_password_here@localhost:5432/epcdjangosite
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost
```

### 5. Database Migration and Setup
```bash
# Navigate to project directory
cd /var/www/epcdjangosite/epcdata

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create media directory structure
mkdir -p media/oscar/img
```

### 6. Copy Missing Image File
```bash
# Copy Oscar's missing image placeholder
cp env/lib/python3.*/site-packages/oscar/static/oscar/img/image_not_found.jpg media/oscar/img/
cp env/lib/python3.*/site-packages/oscar/static/oscar/img/image_not_found.jpg media/
```

### 7. Set Permissions
```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/epcdjangosite
sudo chmod -R 755 /var/www/epcdjangosite

# Set specific permissions for media
sudo chmod -R 775 /var/www/epcdjangosite/epcdata/media
```

### 8. Configure Gunicorn
Create `/var/www/epcdjangosite/gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
```

### 9. Setup Supervisor
Create `/etc/supervisor/conf.d/epcdjangosite.conf`:
```ini
[program:epcdjangosite]
command=/var/www/epcdjangosite/env/bin/gunicorn --config /var/www/epcdjangosite/gunicorn.conf.py epcdata.wsgi:application
directory=/var/www/epcdjangosite/epcdata
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/epcdjangosite.log
```

### 10. Configure Nginx
Create `/etc/nginx/sites-available/epcdjangosite`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 50M;
    
    location /static/ {
        alias /var/www/epcdjangosite/epcdata/static/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/epcdjangosite/epcdata/media/;
        expires 30d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 11. Enable and Start Services
```bash
# Enable nginx site
sudo ln -s /etc/nginx/sites-available/epcdjangosite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start epcdjangosite
```

## Data Migration

### If migrating from existing database:
1. **Export data from current system:**
   ```bash
   # From your current server
   pg_dump epcdjangosite > epcdjangosite_backup.sql
   ```

2. **Import on new server:**
   ```bash
   # On new server
   sudo -u postgres psql epcdjangosite < epcdjangosite_backup.sql
   ```

3. **Run Django migrations to ensure schema is up to date:**
   ```bash
   python manage.py migrate
   ```

### Verify Installation
- Visit: `http://your-domain.com/admin/` (Django admin)
- Visit: `http://your-domain.com/dashboard/` (Oscar dashboard)
- Visit: `http://your-domain.com/` (Your homepage)

## Post-Installation
1. Set up SSL with Let's Encrypt
2. Configure regular database backups
3. Set up monitoring and logging
4. Configure email settings in Django settings

## Key Features Available
- **Oscar 3.2.4 E-commerce Platform**
- **1,601 Products** with GBP pricing
- **Native Oscar Dashboard** for product management
- **Full catalogue management**
- **Order processing system**
- **Customer account management** with basket integration
- **Partner/supplier management**
- **Stock and inventory tracking**
- **Shopping basket functionality** with proper context processors

## Important Configuration Notes
- **Oscar Context Processors**: Required for basket, search, and customer functionality
- **Oscar Middleware**: BasketMiddleware essential for shopping cart features
- **Template Settings**: All Oscar context processors configured in settings
- **Media Files**: Oscar image placeholders properly configured

## Support
Your Oscar e-commerce platform is now ready for production with all data migrated and full functionality available.
