#!/usr/bin/env python
"""
Test script to verify server IP detection and environment switching
"""
import os
import socket
from pathlib import Path

def detect_production_server():
    try:
        # Get the server's IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"Current hostname: {hostname}")
        print(f"Current local IP: {local_ip}")
        
        # Check if running on the production VPS IP
        production_ips = ['80.95.207.42']
        
        # Also check for environment variables that indicate VPS deployment
        vps_indicators = [
            os.environ.get('SERVER_IP') == '80.95.207.42',
            os.environ.get('HOSTNAME', '').lower().find('vps') != -1,
            os.environ.get('HOSTNAME', '').lower().find('server') != -1,
        ]
        
        print(f"Production IPs to check: {production_ips}")
        print(f"IP match: {local_ip in production_ips}")
        print(f"VPS indicators: {vps_indicators}")
        print(f"Any VPS indicator true: {any(vps_indicators)}")
        
        is_production = local_ip in production_ips or any(vps_indicators)
        return is_production
    except Exception as e:
        print(f"Error in detection: {e}")
        return False

if __name__ == "__main__":
    print("=== Server Detection Test ===")
    is_production = detect_production_server()
    
    print(f"\nResult: {'PRODUCTION' if is_production else 'LOCAL'} environment detected")
    
    if is_production:
        print("✅ Would use .env.production with N0rfolk password")
    else:
        print("✅ Would use .env with motorpartsdata + letmein123")
    
    # Check which files exist
    print("\n=== Environment Files ===")
    BASE_DIR = Path(__file__).resolve().parent
    files_to_check = ['.env', '.env.production', '.env.production.disabled', '.prod', '.prod.disabled']
    
    for file in files_to_check:
        path = BASE_DIR / file
        exists = "✅" if path.exists() else "❌"
        print(f"{exists} {file}")
