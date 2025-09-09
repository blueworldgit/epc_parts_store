"""
Custom shipping repository that provides weight-based shipping methods
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
        print(f"DEBUG: WeightBasedShippingMethod.calculate called with basket: {basket}")
        
        # Calculate total weight of all items in basket
        total_weight = self._calculate_total_weight(basket)
        print(f"DEBUG: Total weight calculated: {total_weight}kg")
        
        # Determine which weight band applies
        shipping_cost = self._get_shipping_cost_for_weight(total_weight)
        print(f"DEBUG: Shipping cost for {total_weight}kg: £{shipping_cost}")
        
        # Return the price
        price = prices.Price(
            currency=basket.currency,
            excl_tax=shipping_cost,
            incl_tax=shipping_cost  # No tax on shipping
        )
        print(f"DEBUG: Returning price object: {price}")
        return price

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
    Free shipping option (for admin/promotional purposes)
    """
    code = 'free'
    name = 'Free Shipping'
    description = 'No shipping charge'


class ExpressShippingMethod(methods.FixedPrice):
    """
    Express shipping option (hidden from users but keeps shipping selection page visible)
    """
    code = 'express'
    name = 'Express Shipping'
    description = 'Next working day delivery'
    charge_excl_tax = Decimal('19.95')
    charge_incl_tax = Decimal('19.95')


# Repository class to provide available shipping methods
class Repository(object):
    """
    Custom repository for weight-based shipping methods
    This overrides Oscar's default shipping repository
    """

    def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, **kwargs):
        """
        Return available shipping methods
        """
        print(f"DEBUG: get_available_shipping_methods called with basket: {basket}")
        methods_list = []
        
        # Always offer weight-based shipping
        method = WeightBasedShippingMethod()
        print(f"DEBUG: Created WeightBasedShippingMethod: {method}")
        
        # Calculate the charge for this method with the basket
        if basket:
            try:
                charge = method.calculate(basket)
                print(f"DEBUG: Calculated charge: {charge}")
                # Set the calculated charge on the method
                method.charge_excl_tax = charge.excl_tax
                method.charge_incl_tax = charge.incl_tax
                print(f"DEBUG: Set method charges - excl_tax: {method.charge_excl_tax}, incl_tax: {method.charge_incl_tax}")
            except Exception as e:
                print(f"DEBUG: Error calculating charge: {e}")
                # Fallback to default charge
                method.charge_excl_tax = Decimal('11.95')
                method.charge_incl_tax = Decimal('11.95')
        
        methods_list.append(method)
        
        # Add express shipping option (will be hidden with CSS)
        express_method = ExpressShippingMethod()
        methods_list.append(express_method)
        
        print(f"DEBUG: Returning methods_list: {methods_list}")
        return methods_list

    def get_shipping_methods(self, basket, user=None, shipping_addr=None, **kwargs):
        """
        Alias for get_available_shipping_methods (Oscar sometimes calls this instead)
        """
        return self.get_available_shipping_methods(basket, user, shipping_addr, **kwargs)

    def get_default_shipping_method(self, basket, user=None, shipping_addr=None, **kwargs):
        """
        Return the default shipping method
        """
        methods_list = self.get_available_shipping_methods(basket, user, shipping_addr, **kwargs)
        return methods_list[0] if methods_list else None
