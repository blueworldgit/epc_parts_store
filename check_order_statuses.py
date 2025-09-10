#!/usr/bin/env python
"""
Check available order statuses in Django Oscar
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epcdata'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

django.setup()

from oscar.core.loading import get_model

def check_order_statuses():
    """Check what order statuses are available"""
    try:
        from oscar.apps.order.models import Order
        from oscar.apps.order import status
        
        print("🔍 Checking Django Oscar order statuses...")
        
        # Check if there's a status configuration
        if hasattr(status, 'ORDER_STATUS_CHOICES'):
            print("ORDER_STATUS_CHOICES:")
            for choice in status.ORDER_STATUS_CHOICES:
                print(f"  - {choice}")
        
        # Check for common statuses
        common_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Complete', 'Cancelled', 'Paid']
        
        print("\\nTesting common order statuses:")
        Order = get_model('order', 'Order')
        test_order = Order.objects.first()
        
        if test_order:
            current_status = test_order.status
            print(f"Current order status: '{current_status}'")
            
            for test_status in common_statuses:
                try:
                    # Test without actually changing
                    test_order._old_status = test_order.status
                    test_order.status = test_status
                    test_order.clean()
                    print(f"  ✅ '{test_status}' - Valid")
                    test_order.status = test_order._old_status  # Restore
                except Exception as e:
                    print(f"  ❌ '{test_status}' - Invalid: {e}")
                    test_order.status = test_order._old_status  # Restore
        
        # Check Oscar's default pipeline statuses
        try:
            from oscar.apps.order.models import OrderStatus
            statuses = OrderStatus.objects.all()
            print(f"\\nOrderStatus objects in database: {len(statuses)}")
            for status_obj in statuses:
                print(f"  - {status_obj.name} (slug: {status_obj.slug})")
        except Exception as e:
            print(f"\\nNo OrderStatus model or error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    check_order_statuses()
