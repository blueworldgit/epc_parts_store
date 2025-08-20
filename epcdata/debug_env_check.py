#!/usr/bin/env python
"""
Debug script to check what Worldpay environment variables are loaded
Run this on your server to see exactly what credentials Django is seeing
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

def check_worldpay_config():
    """Check all Worldpay-related configuration"""
    print("🌍 WORLDPAY CONFIGURATION DEBUG")
    print("=" * 50)
    
    # Check environment variables directly from os.environ
    print("\n📍 ENVIRONMENT VARIABLES (from os.environ):")
    worldpay_env_vars = [var for var in os.environ.keys() if 'WORLDPAY' in var or 'GATEWAY' in var]
    for var in sorted(worldpay_env_vars):
        value = os.environ[var]
        if 'PASSWORD' in var:
            masked_value = '*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '*' * len(value)
            print(f"   {var} = {masked_value}")
        else:
            print(f"   {var} = {value}")
    
    if not worldpay_env_vars:
        print("   ❌ NO WORLDPAY ENVIRONMENT VARIABLES FOUND!")
    
    # Check Django settings
    print("\n⚙️  DJANGO SETTINGS:")
    worldpay_settings = [
        'WORLDPAY_TEST_MODE',
        'WORLDPAY_GATEWAY_URL',
        'WORLDPAY_GATEWAY_USERNAME', 
        'WORLDPAY_GATEWAY_PASSWORD',
        'WORLDPAY_GATEWAY_ENTITY_ID',
        'WORLDPAY_USERNAME',  # Old variable
        'WORLDPAY_PASSWORD',  # Old variable
        'WORLDPAY_ENTITY_ID', # Old variable
        'WORLDPAY_URL',       # Old variable
    ]
    
    for setting in worldpay_settings:
        try:
            value = getattr(settings, setting)
            if 'PASSWORD' in setting:
                masked_value = '*' * (len(str(value)) - 4) + str(value)[-4:] if len(str(value)) > 4 else '*' * len(str(value))
                print(f"   {setting} = {masked_value}")
            else:
                print(f"   {setting} = {value}")
        except AttributeError:
            print(f"   {setting} = NOT SET")
    
    # Check what the facade will actually use
    print("\n🏗️  GATEWAY FACADE CONFIGURATION:")
    try:
        from payment.gateway_facade import WorldpayGatewayFacade
        facade = WorldpayGatewayFacade()
        print(f"   API URL: {facade.api_url}")
        print(f"   Username: {facade.username}")
        password_masked = '*' * (len(facade.password) - 4) + facade.password[-4:] if len(facade.password) > 4 else '*' * len(facade.password)
        print(f"   Password: {password_masked}")
        print(f"   Entity ID: {facade.entity_id}")
        
        # Check for empty values
        empty_fields = []
        if not facade.username:
            empty_fields.append("USERNAME")
        if not facade.password:
            empty_fields.append("PASSWORD")
        if not facade.entity_id:
            empty_fields.append("ENTITY_ID")
        if not facade.api_url:
            empty_fields.append("API_URL")
            
        if empty_fields:
            print(f"   ❌ EMPTY FIELDS: {', '.join(empty_fields)}")
        else:
            print("   ✅ All fields have values")
            
    except Exception as e:
        print(f"   ❌ ERROR loading facade: {e}")
    
    # Check current working directory and .env files
    print(f"\n📁 CURRENT DIRECTORY: {os.getcwd()}")
    print("📄 ENVIRONMENT FILES:")
    env_files = ['.env', '.env.production', '.env.local', '.prod']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   ✅ {env_file} EXISTS")
        else:
            print(f"   ❌ {env_file} NOT FOUND")

if __name__ == "__main__":
    check_worldpay_config()
