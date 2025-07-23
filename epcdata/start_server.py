#!/usr/bin/env python3
"""
Simple test to start the Django server
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
