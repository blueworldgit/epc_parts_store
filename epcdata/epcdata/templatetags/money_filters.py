"""
Money and VAT calculation template filters using precise_money
"""
from django import template
try:
    from precise_money import Money
    PRECISE_MONEY_AVAILABLE = True
except ImportError:
    PRECISE_MONEY_AVAILABLE = False
    from decimal import Decimal, ROUND_HALF_UP

register = template.Library()

@register.filter
def pence_to_pounds(value):
    """
    Convert pence (integer) to pounds (decimal) with proper precision
    Example: 2781 -> 27.81
    """
    if value is None:
        return "0.00"
    
    try:
        if PRECISE_MONEY_AVAILABLE:
            # Use precise_money for exact calculations
            pence_money = Money(value, 'pence')
            pounds = pence_money.convert_to('pounds')
            return f"{pounds:.2f}"
        else:
            # Fallback to Decimal
            from decimal import Decimal, ROUND_HALF_UP
            pence = Decimal(str(value))
            pounds = pence / Decimal('100')
            return pounds.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError):
        return "0.00"

@register.filter
def add_precise(value1, value2):
    """
    Add two decimal values with exact precision
    """
    if value1 is None:
        value1 = 0
    if value2 is None:
        value2 = 0
    
    try:
        if PRECISE_MONEY_AVAILABLE:
            money1 = Money(value1, 'GBP')
            money2 = Money(value2, 'GBP') 
            result = money1 + money2
            return float(result)
        else:
            # Fallback to Decimal
            from decimal import Decimal, ROUND_HALF_UP
            dec1 = Decimal(str(value1))
            dec2 = Decimal(str(value2))
            result = dec1 + dec2
            return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError):
        return 0.00

@register.filter
def vat_calculation(subtotal_ex_vat):
    """
    Calculate 20% VAT on a subtotal using precise arithmetic
    """
    try:
        if PRECISE_MONEY_AVAILABLE:
            subtotal = Money(subtotal_ex_vat, 'GBP')
            vat = subtotal * 0.20
            return f"{vat:.2f}"
        else:
            # Fallback to Decimal
            from decimal import Decimal, ROUND_HALF_UP
            subtotal = Decimal(str(subtotal_ex_vat))
            vat = subtotal * Decimal('0.20')
            return vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError):
        return "0.00"
