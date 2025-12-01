#!/bin/bash
# Get recent logs related to 3DS payment flow

echo "============================================================"
echo "DJANGO/GUNICORN LOGS - Last 200 lines with 3DS/payment keywords"
echo "============================================================"
sudo journalctl -u vanparts-direct --no-pager --since "10 minutes ago" -n 200 | grep -E "3DS|callback|challenge|payment|Gateway|POST.*card-form|GET.*threeds" -i --color=never

echo ""
echo "============================================================"
echo "NGINX ACCESS LOGS - Last 50 payment-related requests"
echo "============================================================"
sudo tail -50 /var/log/nginx/access.log | grep -E "payment|threeds|card-form|gateway" --color=never

echo ""
echo "============================================================"
echo "NGINX ERROR LOGS - Last 50 lines"
echo "============================================================"
sudo tail -50 /var/log/nginx/error.log

echo ""
echo "============================================================"
echo "GUNICORN ERROR LOGS - If exists"
echo "============================================================"
if [ -f "/var/log/gunicorn/error.log" ]; then
    sudo tail -100 /var/log/gunicorn/error.log | grep -E "3DS|callback|challenge|payment" -i --color=never
else
    echo "Gunicorn error log not found at /var/log/gunicorn/error.log"
fi

echo ""
echo "============================================================"
echo "ALL RECENT DJANGO LOGS - Last 100 lines (unfiltered)"
echo "============================================================"
sudo journalctl -u vanparts-direct --no-pager --since "5 minutes ago" -n 100 --no-hostname

echo ""
echo "============================================================"
echo "DJANGO DEBUG LOG FILE - Last 200 lines"
echo "============================================================"
if [ -f "/home/rentals/epc_parts_store/django_debug.log" ]; then
    sudo tail -200 /home/rentals/epc_parts_store/django_debug.log
else
    echo "Log file not found at /home/rentals/epc_parts_store/django_debug.log"
    echo "Run: sudo touch /home/rentals/epc_parts_store/django_debug.log"
    echo "Then: sudo chown rentals:rentals /home/rentals/epc_parts_store/django_debug.log"
fi

echo ""
echo "============================================================"
echo "DONE - Copy all output above"
echo "============================================================"
