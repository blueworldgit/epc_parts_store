"""
Custom shipping methods for weight-based pricing
"""
from decimal import Decimal
from oscar.apps.shipping import methods
from oscar.core import prices
from oscar.apps.catalogue.models import ProductAttribute


class WeightBasedShippingMethod(methods.Base):
    """
    Weight-based shipping method with fixed price bands
    """
    code = 'weight_based'
    name = 'Standard Shipping'
    description = 'Shipping calculated by total weight'

    # Define weight bands and their costs
    WEIGHT_BANDS = [
        (Decimal('0'), Decimal('24.9'), Decimal('11.95')),    # 0-24.9kg → £11.95
        (Decimal('25'), Decimal('49.9'), Decimal('23.90')),   # 25-49.9kg → £23.90
        (Decimal('50'), Decimal('74.9'), Decimal('35.95')),   # 50-74.9kg → £35.95
    ]

    def calculate(self, basket):
        """
        Calculate shipping cost based on total basket weight
        """
        # Calculate total weight of all items in basket
        total_weight = self._calculate_total_weight(basket)
        
        # Determine which weight band applies
        shipping_cost = self._get_shipping_cost_for_weight(total_weight)
        
        # Return the price
        return prices.Price(
            currency=basket.currency,
            excl_tax=shipping_cost,
            incl_tax=shipping_cost  # No tax on shipping
        )

    def _calculate_total_weight(self, basket):
        """
        Calculate the total weight of all items in the basket
        """
        total_weight = Decimal('0')
        
        try:
            # Get the weight attribute
            weight_attr = ProductAttribute.objects.get(code='weight')
            
            for line in basket.all_lines():
                product = line.product
                quantity = line.quantity
                
                # Get the weight attribute value for this product
                try:
                    weight_value = product.attribute_values.get(attribute=weight_attr)
                    if weight_value.value_float:
                        item_weight = Decimal(str(weight_value.value_float))
                        total_weight += item_weight * quantity
                except:
                    # If no weight attribute, assume 0kg for this item
                    pass
                    
        except ProductAttribute.DoesNotExist:
            # If weight attribute doesn't exist, return 0
            pass
            
        return total_weight

    def _get_shipping_cost_for_weight(self, weight):
        """
        Get the shipping cost for the given weight based on weight bands
        """
        for min_weight, max_weight, cost in self.WEIGHT_BANDS:
            if min_weight <= weight <= max_weight:
                return cost
        
        # If weight exceeds all bands, return the highest band cost
        return self.WEIGHT_BANDS[-1][2]


class FreeShippingMethod(methods.Free):
    """
    Free shipping option (TEMPORARY FOR TESTING - REMOVE LATER)
    """
    code = 'free'
    name = 'Free Shipping (Testing)'
    description = 'No shipping charge - Testing purposes only'


# Repository class to provide available shipping methods
class CustomShippingRepository(object):
    """
    Custom repository for weight-based shipping methods
    """

    def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, **kwargs):
        """
        Return available shipping methods
        """
        methods_list = []
        
        # Always offer weight-based shipping
        methods_list.append(WeightBasedShippingMethod())
        
        # TEMPORARY FOR TESTING: Offer free shipping to all users
        # TODO: Remove this later - only for testing to avoid card charges
        methods_list.append(FreeShippingMethod())
            
        return methods_list

    def get_default_shipping_method(self, basket, user=None, shipping_addr=None, **kwargs):
        """
        Return the default shipping method
        """
        methods_list = self.get_available_shipping_methods(basket, user, shipping_addr, **kwargs)
        return methods_list[0] if methods_list else None
