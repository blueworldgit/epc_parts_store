"""
Custom address models to override phone number validation
"""
from django.db import models
from oscar.apps.address import abstract_models


class AbstractUserAddress(abstract_models.AbstractUserAddress):
    """
    Override Oscar's AbstractUserAddress to use a simple CharField for phone_number
    """
    
    # Override phone_number field to use CharField instead of PhoneNumberField
    phone_number = models.CharField(
        max_length=32, 
        blank=True,
        verbose_name="Phone number",
        help_text="Enter any phone number format"
    )
    
    class Meta(abstract_models.AbstractUserAddress.Meta):
        abstract = True


class UserAddress(AbstractUserAddress):
    """
    Concrete model for user addresses with simple phone validation
    """
    pass
