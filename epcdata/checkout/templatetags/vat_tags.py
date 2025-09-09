from django import template
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

register = template.Library()

@register.filter
def calculate_vat(price, vat_rate=None):
    """
    Calculate VAT amount from a price including VAT
    Assumes price includes VAT and calculates the VAT component
    """
    if not price:
        return Decimal('0.00')
    
    try:
        price_decimal = Decimal(str(price))
        if vat_rate is None:
            vat_rate = getattr(settings, 'UK_VAT_RATE', Decimal('0.20'))
        else:
            vat_rate = Decimal(str(vat_rate))
        
        # Calculate VAT from price that includes VAT
        # VAT = (price_inc_vat * vat_rate) / (1 + vat_rate)
        vat_amount = (price_decimal * vat_rate) / (Decimal('1') + vat_rate)
        return vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')

@register.filter
def calculate_excl_vat(price, vat_rate=None):
    """
    Calculate price excluding VAT from a price including VAT
    """
    if not price:
        return Decimal('0.00')
    
    try:
        price_decimal = Decimal(str(price))
        if vat_rate is None:
            vat_rate = getattr(settings, 'UK_VAT_RATE', Decimal('0.20'))
        else:
            vat_rate = Decimal(str(vat_rate))
        
        # Calculate price excluding VAT
        # Price excl VAT = price_inc_vat / (1 + vat_rate)
        price_excl_vat = price_decimal / (Decimal('1') + vat_rate)
        return price_excl_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')

@register.filter
def add_vat(price, vat_rate=None):
    """
    Add VAT to a price excluding VAT
    """
    if not price:
        return Decimal('0.00')
    
    try:
        price_decimal = Decimal(str(price))
        if vat_rate is None:
            vat_rate = getattr(settings, 'UK_VAT_RATE', Decimal('0.20'))
        else:
            vat_rate = Decimal(str(vat_rate))
        
        # Calculate price including VAT
        price_inc_vat = price_decimal * (Decimal('1') + vat_rate)
        return price_inc_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')

@register.simple_tag
def vat_breakdown(total_inc_vat, shipping_inc_vat=None):
    """
    Calculate complete VAT breakdown for order totals
    Returns dict with subtotal_excl_vat, shipping_excl_vat, vat_amount, total_inc_vat
    """
    vat_rate = getattr(settings, 'UK_VAT_RATE', Decimal('0.20'))
    
    try:
        total_decimal = Decimal(str(total_inc_vat)) if total_inc_vat else Decimal('0')
        shipping_decimal = Decimal(str(shipping_inc_vat)) if shipping_inc_vat else Decimal('0')
        
        # Calculate excluding VAT amounts
        total_excl_vat = total_decimal / (Decimal('1') + vat_rate)
        shipping_excl_vat = shipping_decimal / (Decimal('1') + vat_rate)
        subtotal_excl_vat = total_excl_vat - shipping_excl_vat
        
        # Calculate VAT amounts
        total_vat = total_decimal - total_excl_vat
        
        return {
            'subtotal_excl_vat': subtotal_excl_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'shipping_excl_vat': shipping_excl_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'vat_amount': total_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'total_inc_vat': total_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        }
    except (ValueError, TypeError, AttributeError):
        return {
            'subtotal_excl_vat': Decimal('0.00'),
            'shipping_excl_vat': Decimal('0.00'),
            'vat_amount': Decimal('0.00'),
            'total_inc_vat': Decimal('0.00'),
        }
