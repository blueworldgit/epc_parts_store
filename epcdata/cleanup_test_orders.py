"""
Clean up test order to start fresh
"""
import os
import sys
import django
import logging

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.core.loading import get_model

Order = get_model('order', 'Order')

logger.info("="*60)
logger.info("TEST ORDER CLEANUP")
logger.info("="*60)

# Delete recent test orders
test_orders = Order.objects.filter(number__startswith='100001-4').order_by('-date_placed')[:10]

logger.info(f"\nFound {test_orders.count()} test orders:")
for order in test_orders:
    logger.info(f"  - {order.number} (£{order.total_incl_tax}) - {order.status}")

if test_orders.count() > 0:
    logger.info(f"\nDeleting {test_orders.count()} orders...")
    count = test_orders.count()
    test_orders.delete()
    logger.info(f"✅ Deleted {count} test orders")
else:
    logger.info("\nNo test orders to delete")

logger.info("="*60)
