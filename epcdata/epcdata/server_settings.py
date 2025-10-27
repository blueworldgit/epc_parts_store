"""
Server-specific settings for VPS deployment
This file forces production mode without requiring environment variables
"""
import os

# Force production environment
os.environ['DJANGO_ENV'] = 'production'

# Import main settings after setting environment
from .settings import *

print("🎯 VPS SERVER: Forcing production mode via server_settings.py")