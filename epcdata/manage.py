#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    
    # Auto-detect VPS server and set production environment
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Check if running on VPS server
        if local_ip in ['80.95.207.45'] or hostname.lower() == 'rentals':
            os.environ.setdefault('DJANGO_ENV', 'production')
            print(f"🎯 AUTO-DETECTED VPS SERVER: Setting DJANGO_ENV=production (IP: {local_ip}, Host: {hostname})")
    except Exception as e:
        print(f"⚠️ Server detection failed: {e}")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
