#!/usr/bin/env python
import os
import django
from pathlib import Path
from dotenv import load_dotenv

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Load the .env file explicitly
BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / '.env'
print(f"Loading .env from: {env_file}")
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    load_dotenv(env_file)
    print("✅ .env file loaded")
else:
    print("❌ .env file not found")

# Print environment variables
print("\n--- Environment Variables ---")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")

# Set up Django and check what it's using
django.setup()
from django.conf import settings

print("\n--- Django Database Configuration ---")
db_config = settings.DATABASES['default']
print(f"ENGINE: {db_config['ENGINE']}")
print(f"NAME: {db_config['NAME']}")
print(f"USER: {db_config['USER']}")
print(f"PASSWORD: {db_config['PASSWORD']}")
print(f"HOST: {db_config['HOST']}")
print(f"PORT: {db_config['PORT']}")

# Test database connection
print("\n--- Testing Database Connection ---")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    print(f"✅ Database connection successful!")
    print(f"PostgreSQL version: {result[0]}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
