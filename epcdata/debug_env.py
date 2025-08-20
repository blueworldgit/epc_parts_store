#!/usr/bin/env python3
"""
Debug script to check environment variables and Django settings
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

try:
    django.setup()
    from django.conf import settings
    
    print("=== ENVIRONMENT VARIABLES ===")
    print(f"WORLDPAY_USERNAME: {os.environ.get('WORLDPAY_USERNAME', 'NOT SET')}")
    print(f"WORLDPAY_PASSWORD: {os.environ.get('WORLDPAY_PASSWORD', 'NOT SET')}")
    print(f"WORLDPAY_ENTITY_ID: {os.environ.get('WORLDPAY_ENTITY_ID', 'NOT SET')}")
    print(f"WORLDPAY_TEST_MODE: {os.environ.get('WORLDPAY_TEST_MODE', 'NOT SET')}")
    
    print("\n=== DJANGO SETTINGS ===")
    print(f"WORLDPAY_USERNAME: {getattr(settings, 'WORLDPAY_USERNAME', 'NOT SET')}")
    print(f"WORLDPAY_PASSWORD: {getattr(settings, 'WORLDPAY_PASSWORD', 'NOT SET')}")
    print(f"WORLDPAY_ENTITY_ID: {getattr(settings, 'WORLDPAY_ENTITY_ID', 'NOT SET')}")
    print(f"WORLDPAY_TEST_MODE: {getattr(settings, 'WORLDPAY_TEST_MODE', 'NOT SET')}")
    
    print("\n=== .ENV FILE LOCATION ===")
    env_file = project_dir / '.env'
    print(f"Looking for .env at: {env_file}")
    print(f".env file exists: {env_file.exists()}")
    if env_file.exists():
        print(f".env file size: {env_file.stat().st_size} bytes")
    
    print("\n=== PYTHON-DOTENV CHECK ===")
    try:
        from dotenv import load_dotenv
        print("python-dotenv is available")
        # Try loading the .env file explicitly
        loaded = load_dotenv(env_file)
        print(f"load_dotenv result: {loaded}")
    except ImportError:
        print("python-dotenv is NOT installed")
    
    print("\n=== WORLDPAY FACADE TEST ===")
    try:
        from payment.facade import WorldpayHostedFacade
        facade = WorldpayHostedFacade()
        print("WorldpayHostedFacade created successfully")
        
        # Test auth header generation
        auth_header = facade._get_auth_header()
        print(f"Auth header generated: {auth_header[:20]}...")  # Show first 20 chars for security
        
    except Exception as e:
        print(f"Error creating WorldpayHostedFacade: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"Error setting up Django: {e}")
    import traceback
    traceback.print_exc()
