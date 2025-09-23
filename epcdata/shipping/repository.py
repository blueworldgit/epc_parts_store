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

    # Define weight bands and their costs - Comprehensive weight brackets
    WEIGHT_BANDS = [
        (Decimal('0'), Decimal('24.9'), Decimal('11.95')),
        (Decimal('25'), Decimal('49.9'), Decimal('23.90')),
        (Decimal('50'), Decimal('74.9'), Decimal('35.85')),
        (Decimal('75'), Decimal('99.9'), Decimal('47.80')),
        (Decimal('100'), Decimal('124.9'), Decimal('59.75')),
        (Decimal('125'), Decimal('149.9'), Decimal('71.70')),
        (Decimal('150'), Decimal('174.9'), Decimal('83.65')),
        (Decimal('175'), Decimal('199.9'), Decimal('95.60')),
        (Decimal('200'), Decimal('224.9'), Decimal('107.55')),
        (Decimal('225'), Decimal('249.9'), Decimal('119.50')),
        (Decimal('250'), Decimal('274.9'), Decimal('131.45')),
        (Decimal('275'), Decimal('299.9'), Decimal('143.40')),
        (Decimal('300'), Decimal('324.9'), Decimal('155.35')),
        (Decimal('325'), Decimal('349.9'), Decimal('167.30')),
        (Decimal('350'), Decimal('374.9'), Decimal('179.25')),
        (Decimal('375'), Decimal('399.9'), Decimal('191.20')),
        (Decimal('400'), Decimal('424.9'), Decimal('203.15')),
        (Decimal('425'), Decimal('449.9'), Decimal('215.10')),
        (Decimal('450'), Decimal('474.9'), Decimal('227.05')),
        (Decimal('475'), Decimal('499.9'), Decimal('239.00')),
        (Decimal('500'), Decimal('524.9'), Decimal('250.95')),
        (Decimal('525'), Decimal('549.9'), Decimal('262.90')),
        (Decimal('550'), Decimal('574.9'), Decimal('274.85')),
        (Decimal('575'), Decimal('599.9'), Decimal('286.80')),
        (Decimal('600'), Decimal('624.9'), Decimal('298.75')),
        (Decimal('625'), Decimal('649.9'), Decimal('310.70')),
        (Decimal('650'), Decimal('674.9'), Decimal('322.65')),
        (Decimal('675'), Decimal('699.9'), Decimal('334.60')),
        (Decimal('700'), Decimal('724.9'), Decimal('346.55')),
        (Decimal('725'), Decimal('749.9'), Decimal('358.50')),
        (Decimal('750'), Decimal('774.9'), Decimal('370.45')),
        (Decimal('775'), Decimal('799.9'), Decimal('382.40')),
        (Decimal('800'), Decimal('824.9'), Decimal('394.35')),
        (Decimal('825'), Decimal('849.9'), Decimal('406.30')),
        (Decimal('850'), Decimal('874.9'), Decimal('418.25')),
        (Decimal('875'), Decimal('899.9'), Decimal('430.20')),
        (Decimal('900'), Decimal('924.9'), Decimal('442.15')),
        (Decimal('925'), Decimal('949.9'), Decimal('454.10')),
        (Decimal('950'), Decimal('974.9'), Decimal('466.05')),
        (Decimal('975'), Decimal('999.9'), Decimal('478.00')),
        (Decimal('1000'), Decimal('1024.9'), Decimal('489.95')),
        (Decimal('1025'), Decimal('1049.9'), Decimal('501.90')),
        (Decimal('1050'), Decimal('1074.9'), Decimal('513.85')),
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
        print(f"DEBUG: Starting weight calculation for basket with {basket.num_lines} lines")
        
        try:
            # Get the weight attribute
            weight_attr = ProductAttribute.objects.get(code='weight')
            print(f"DEBUG: Found weight attribute: {weight_attr}")
            
            for line in basket.all_lines():
                product = line.product
                quantity = line.quantity
                print(f"DEBUG: Processing product: {product.title} (UPC: {product.upc}, Qty: {quantity})")
                
                # Get the weight attribute value for this product
                try:
                    weight_value = product.attribute_values.get(attribute=weight_attr)
                    print(f"DEBUG: Found weight value: {weight_value.value_float} for {product.title}")
                    if weight_value.value_float:
                        item_weight = Decimal(str(weight_value.value_float))
                        line_weight = item_weight * quantity
                        total_weight += line_weight
                        print(f"DEBUG: Added {line_weight}kg (({item_weight}kg × {quantity}) to total")
                    else:
                        print(f"DEBUG: Weight value is None/0 for {product.title}")
                except Exception as e:
                    # If no weight attribute, assume 0kg for this item
                    print(f"DEBUG: No weight attribute found for {product.title}: {e}")
                    pass
                    
        except ProductAttribute.DoesNotExist:
            # If weight attribute doesn't exist, return 0
            print("DEBUG: Weight attribute 'weight' does not exist in the database!")
            pass
        
        print(f"DEBUG: Final total weight: {total_weight}kg")
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


class FreeShippingMethod(methods.FixedPrice):
    """
    Very cheap shipping option (TEMPORARY FOR TESTING - REMOVE LATER)
    Using £0.20 instead of £0.00 to avoid VAT calculation issues
    """
    code = 'cheap'
    name = 'Cheap Shipping (Testing)'
    description = 'Very low cost shipping - Testing purposes only'
    charge_excl_tax = Decimal('0.20')
    charge_incl_tax = Decimal('0.20')


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
        
        # TEMPORARY FOR TESTING: Add free shipping option for all users
        # TODO: Remove this later - only for testing to avoid card charges
        free_method = FreeShippingMethod()
        methods_list.append(free_method)
        
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
