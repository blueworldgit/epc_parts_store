#!/bin/bash
# PostgreSQL Setup Script for VPS
# Run this script on your VPS to fix the database authentication issue

echo "🔧 Setting up PostgreSQL for Django deployment..."

# 1. Install PostgreSQL if not already installed
if ! command -v psql &> /dev/null; then
    echo "📦 Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib python3-psycopg2
else
    echo "✅ PostgreSQL is already installed"
fi

# 2. Start and enable PostgreSQL service
echo "🚀 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Switch to postgres user and set up database
echo "🗄️ Setting up database and user..."

# Create the database and user
sudo -u postgres psql << EOF
-- Drop database if exists (be careful!)
DROP DATABASE IF EXISTS parts_store;

-- Create the database
CREATE DATABASE parts_store;

-- Create user with password (use the same password as in your .env file)
CREATE USER postgres WITH PASSWORD 'N0rfolk';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE parts_store TO postgres;

-- Make sure the user can create databases (needed for tests)
ALTER USER postgres CREATEDB;

-- Exit
\q
EOF

# 4. Configure PostgreSQL authentication
echo "🔐 Configuring PostgreSQL authentication..."

# Backup the original pg_hba.conf
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup

# Update pg_hba.conf to allow password authentication
sudo sed -i "s/local   all             postgres                                peer/local   all             postgres                                md5/" /etc/postgresql/*/main/pg_hba.conf
sudo sed -i "s/local   all             all                                     peer/local   all             all                                     md5/" /etc/postgresql/*/main/pg_hba.conf

# 5. Restart PostgreSQL to apply changes
echo "🔄 Restarting PostgreSQL..."
sudo systemctl restart postgresql

# 6. Test the connection
echo "🧪 Testing database connection..."
export PGPASSWORD='N0rfolk'
if psql -h localhost -U postgres -d parts_store -c "SELECT version();" &> /dev/null; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed. Let's try alternative approach..."
    
    # Alternative: Set password for postgres user
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'N0rfolk';"
    
    # Test again
    if psql -h localhost -U postgres -d parts_store -c "SELECT version();" &> /dev/null; then
        echo "✅ Database connection successful after password reset!"
    else
        echo "❌ Still having issues. Manual intervention may be needed."
    fi
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure your .env file has the correct database credentials:"
echo "   DB_NAME=parts_store"
echo "   DB_USER=postgres" 
echo "   DB_PASSWORD=N0rfolk"
echo "   DB_HOST=localhost"
echo "   DB_PORT=5432"
echo ""
echo "2. Run your Django deployment script again"
echo ""
