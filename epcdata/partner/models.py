from oscar.apps.partner.abstract_models import (
    AbstractStockRecord, 
    AbstractPartner,
    AbstractStockAlert
)
from django.db import models
from django.utils import timezone


# Extend the StockRecord model to add price tracking
class StockRecord(AbstractStockRecord):
    """
    Extended StockRecord model with price update tracking
    """
    price_updated = models.BooleanField(
        default=False,
        help_text="Indicates if this product's price has been updated from Excel import"
    )
    price_update_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the price was last updated from Excel import"
    )
    price_update_notes = models.TextField(
        blank=True,
        help_text="Notes about the price update (e.g., Excel filename, SKU used)"
    )
    
    def mark_price_updated(self, notes=""):
        """Mark this stock record as price updated with timestamp"""
        self.price_updated = True
        self.price_update_date = timezone.now()
        self.price_update_notes = notes
        self.save(update_fields=['price_updated', 'price_update_date', 'price_update_notes'])
    
    def reset_price_update_flag(self):
        """Reset the price update flag"""
        self.price_updated = False
        self.price_update_date = None
        self.price_update_notes = ""
        self.save(update_fields=['price_updated', 'price_update_date', 'price_update_notes'])


# Use Oscar's default models
class Partner(AbstractPartner):
    pass


class StockAlert(AbstractStockAlert):
    pass
