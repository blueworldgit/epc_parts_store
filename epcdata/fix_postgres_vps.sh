#!/bin/bash
# PostgreSQL Setup Script for VPS
# This script will fix the PostgreSQL authentication issue on your VPS

echo "🔧 Setting up PostgreSQL for EPC Django Oscar Site..."

# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if it's not running
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "📝 Setting up PostgreSQL user and database..."

# Switch to postgres user and run SQL commands
sudo -u postgres psql <<EOF
-- Drop database if it exists (optional - be careful!)
-- DROP DATABASE IF EXISTS epcdataeccomerce;

-- Create database if it doesn't exist
CREATE DATABASE epcdataeccomerce;

-- Set password for postgres user
ALTER USER postgres PASSWORD 'letmein123';

-- Create the database if it doesn't exist (alternative syntax)
SELECT 'CREATE DATABASE epcdataeccomerce' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'epcdataeccomerce')\gexec

-- Grant all privileges to postgres user on the database
GRANT ALL PRIVILEGES ON DATABASE epcdataeccomerce TO postgres;

-- Show current databases
\l

-- Quit
\q
EOF

echo "🔧 Updating PostgreSQL configuration..."

# Update pg_hba.conf to allow password authentication
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup

# Update authentication method for local connections
sudo sed -i 's/local   all             postgres                                peer/local   all             postgres                                md5/' /etc/postgresql/*/main/pg_hba.conf
sudo sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/*/main/pg_hba.conf

# Also update IPv4 local connections if needed
sudo sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' /etc/postgresql/*/main/pg_hba.conf

echo "🔄 Restarting PostgreSQL..."
sudo systemctl restart postgresql

echo "✅ Testing PostgreSQL connection..."
# Test the connection
PGPASSWORD=letmein123 psql -h localhost -U postgres -d epcdataeccomerce -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL setup completed successfully!"
    echo "Database: epcdataeccomerce"
    echo "User: postgres"
    echo "Password: letmein123"
    echo "You can now run your Django migrations."
else
    echo "❌ PostgreSQL connection test failed. Please check the configuration."
fi

echo "📋 Next steps:"
echo "1. Navigate to your Django project directory"
echo "2. Activate your virtual environment"
echo "3. Run: python manage.py migrate"
echo "4. Run: python manage.py collectstatic --noinput"
