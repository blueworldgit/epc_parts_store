#!/usr/bin/env python
"""
Simple script to test order creation
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

import requests

try:
    response = requests.get('http://localhost:8000/payment/debug/test-order/')
    print(f"Status: {response.status_code}")
    print("Response:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
