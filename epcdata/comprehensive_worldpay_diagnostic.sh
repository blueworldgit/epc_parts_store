#!/bin/bash
# Comprehensive Worldpay Configuration Diagnostic Script
# This will show us exactly what's happening with environment loading
# Run this on your Linux server and send the complete output

echo "🔍 WORLDPAY CONFIGURATION DIAGNOSTIC REPORT"
echo "============================================="
echo "Timestamp: $(date)"
echo "Server: $(hostname)"
echo "User: $(whoami)"
echo "Current Directory: $(pwd)"
echo ""

echo "📁 1. ENVIRONMENT FILES CHECK"
echo "------------------------------"
echo "Looking for environment files..."
for env_file in .env .env.production .env.local .prod .env.server; do
    if [ -f "$env_file" ]; then
        echo "✅ $env_file EXISTS"
        echo "   Size: $(wc -c < "$env_file") bytes"
        echo "   Modified: $(stat -c %y "$env_file")"
        echo "   Permissions: $(ls -la "$env_file" | awk '{print $1, $3, $4}')"
    else
        echo "❌ $env_file NOT FOUND"
    fi
done
echo ""

echo "📋 2. ENVIRONMENT FILE CONTENTS"
echo "--------------------------------"
if [ -f ".env.production" ]; then
    echo "Contents of .env.production (WORLDPAY lines only):"
    grep -n -E "WORLDPAY|GATEWAY" .env.production || echo "No WORLDPAY variables found in .env.production"
    echo ""
    echo "Full .env.production file (first 50 lines):"
    head -50 .env.production | nl
else
    echo "❌ .env.production file not found!"
fi
echo ""

echo "🔧 3. CURRENT ENVIRONMENT VARIABLES"
echo "------------------------------------"
echo "Current environment variables (WORLDPAY related):"
env | grep -E "WORLDPAY|GATEWAY" | sort || echo "No WORLDPAY environment variables found"
echo ""

echo "🐍 4. PYTHON/DJANGO DIAGNOSTIC"
echo "-------------------------------"
echo "Python version: $(python3 --version 2>/dev/null || python --version 2>/dev/null || echo 'Python not found')"
echo "Which python: $(which python3 2>/dev/null || which python 2>/dev/null || echo 'Python not found')"
echo ""

# Check if we can run Django commands
if [ -f "manage.py" ]; then
    echo "✅ Django manage.py found"
    echo "Testing Django settings access..."
    
    # Test Django settings
    python3 manage.py shell -c "
import os
from django.conf import settings
print('🔍 Django Settings Check:')
print(f'DEBUG: {getattr(settings, \"DEBUG\", \"NOT_SET\")}')
print(f'ALLOWED_HOSTS: {getattr(settings, \"ALLOWED_HOSTS\", \"NOT_SET\")}')
print('')
print('🌍 Worldpay Settings in Django:')
worldpay_settings = [
    'WORLDPAY_TEST_MODE',
    'WORLDPAY_GATEWAY_URL', 
    'WORLDPAY_GATEWAY_USERNAME',
    'WORLDPAY_GATEWAY_PASSWORD',
    'WORLDPAY_GATEWAY_ENTITY_ID',
    'WORLDPAY_USERNAME',
    'WORLDPAY_PASSWORD', 
    'WORLDPAY_ENTITY_ID',
    'WORLDPAY_URL'
]
for setting in worldpay_settings:
    try:
        value = getattr(settings, setting)
        if 'PASSWORD' in setting:
            masked = '*' * (len(str(value)) - 4) + str(value)[-4:] if len(str(value)) > 4 else '*' * len(str(value))
            print(f'{setting} = {masked}')
        else:
            print(f'{setting} = {value}')
    except AttributeError:
        print(f'{setting} = NOT_SET')
print('')
print('🔧 Environment Variables as seen by Django:')
env_vars = [k for k in os.environ.keys() if 'WORLDPAY' in k or 'GATEWAY' in k]
for var in sorted(env_vars):
    value = os.environ[var]
    if 'PASSWORD' in var:
        masked = '*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '*' * len(value)
        print(f'{var} = {masked}')
    else:
        print(f'{var} = {value}')
if not env_vars:
    print('❌ NO WORLDPAY ENVIRONMENT VARIABLES FOUND')
" 2>/dev/null || echo "❌ Failed to run Django shell command"
else
    echo "❌ Django manage.py not found in current directory"
fi
echo ""

echo "🏗️ 5. WEB SERVER PROCESS CHECK"
echo "-------------------------------"
echo "Looking for running web server processes..."
ps aux | grep -E "(gunicorn|uwsgi|apache|nginx|python.*manage|django)" | grep -v grep || echo "No obvious web server processes found"
echo ""

echo "🔄 6. SYSTEMD SERVICES CHECK"
echo "-----------------------------"
echo "Checking for Django/web-related systemd services..."
sudo systemctl list-units --type=service --state=running | grep -E "(django|gunicorn|uwsgi|apache|nginx)" || echo "No obvious Django services found"
echo ""

echo "👀 7. SUPERVISOR PROCESSES CHECK"
echo "---------------------------------"
if command -v supervisorctl &> /dev/null; then
    echo "Supervisor processes:"
    sudo supervisorctl status || echo "Could not get supervisor status"
else
    echo "Supervisor not installed or not found"
fi
echo ""

echo "📊 8. LOG FILES CHECK"
echo "---------------------"
echo "Looking for recent log entries..."
# Common log locations
for log_path in "/var/log/django" "/var/log/gunicorn" "/var/log/uwsgi" "/var/log/apache2" "/var/log/nginx" "/var/log/supervisor" "logs" "log"; do
    if [ -d "$log_path" ]; then
        echo "📁 Found log directory: $log_path"
        ls -la "$log_path" | head -10
        echo ""
        # Look for recent errors
        find "$log_path" -name "*.log" -mtime -1 -exec echo "Recent log: {}" \; -exec tail -5 {} \; 2>/dev/null | head -20
    fi
done
echo ""

echo "🔍 9. DJANGO PROJECT STRUCTURE"
echo "-------------------------------"
echo "Current directory structure:"
ls -la | head -20
echo ""
echo "Looking for Django apps..."
find . -name "settings.py" -o -name "wsgi.py" -o -name "urls.py" | head -10
echo ""

echo "⚡ 10. LIVE TEST OF WORLDPAY FACADE"
echo "-----------------------------------"
if [ -f "manage.py" ]; then
    echo "Testing Worldpay facade initialization..."
    python3 manage.py shell -c "
try:
    from payment.gateway_facade import WorldpayGatewayFacade
    print('✅ Successfully imported WorldpayGatewayFacade')
    facade = WorldpayGatewayFacade()
    print(f'API URL: {facade.api_url}')
    print(f'Username: {facade.username}')
    password_masked = '*' * (len(facade.password) - 4) + facade.password[-4:] if len(facade.password) > 4 else '*' * len(facade.password)
    print(f'Password: {password_masked}')
    print(f'Entity ID: {facade.entity_id}')
    
    # Check for empty values
    empty_fields = []
    if not facade.username: empty_fields.append('USERNAME')
    if not facade.password: empty_fields.append('PASSWORD')
    if not facade.entity_id: empty_fields.append('ENTITY_ID')
    if not facade.api_url: empty_fields.append('API_URL')
    
    if empty_fields:
        print(f'❌ EMPTY FIELDS: {\"|\".join(empty_fields)}')
    else:
        print('✅ All fields have values')
        
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    print(traceback.format_exc())
" 2>/dev/null || echo "❌ Failed to test Worldpay facade"
else
    echo "❌ Cannot test - manage.py not found"
fi
echo ""

echo "🎯 11. FINAL RECOMMENDATIONS"
echo "-----------------------------"
echo "Based on this diagnostic, check for:"
echo "1. Are environment variables loaded into Django settings?"
echo "2. Is the correct .env file being used?"
echo "3. Is Django properly restarted after environment changes?"
echo "4. Are there any permission issues with environment files?"
echo ""
echo "📋 END OF DIAGNOSTIC REPORT"
echo "============================"
