#!/bin/bash

# New Server Deployment Script
# Run this script on the new server after git clone

echo "🚀 Starting deployment on new server..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# Install Node.js and npm (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Database setup - using remote database on 80.95.207.42
echo "📋 Database Configuration:"
echo "   Database: vanrentalsnewdb on 80.95.207.42"
echo "   Username: epc_user"
echo "   Note: Database already exists on remote server"

# Create Python virtual environment
python3 -m venv env
source env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Environment file is already configured as .env.production
echo "📋 Using .env.production for new server configuration"

# Update environment file with actual server details
echo "⚠️  Remember to update .env.production with:"
echo "2. Update .env.production with your domain name"
echo "   - Generate a new SECRET_KEY"
echo "   - Server IP and database are already configured"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (optional)
echo "Create a superuser account:"
python manage.py createsuperuser

# Copy nginx configuration
sudo cp newserver.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/newserver.conf /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Install and configure SSL certificate (run this manually after updating domain)
echo "📋 Next steps:"
echo "1. Update newserver.conf with your actual domain name"
echo "2. Update .env.newserver with your domain (IP and DB already configured)"
echo "3. Ensure PostgreSQL on 80.95.207.42 allows connections from 80.95.207.45"
echo "4. Run: sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo "5. Start the Django app: python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🗄️ Database: vanrentalsnewdb on 80.95.207.42"
echo "👤 User: epc_user"

echo "✅ Deployment setup complete!"