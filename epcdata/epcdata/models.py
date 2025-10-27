from django.db import models
from oscar.apps.catalogue.models import ProductAttributeValue

# Create a proxy model for weight-specific admin
class WeightAttributeValue(ProductAttributeValue):
    class Meta:
        proxy = True
        verbose_name = "Product Weight"
        verbose_name_plural = "Product Weights"