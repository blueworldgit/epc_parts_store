from django.http import JsonResponse
from django.conf import settings
from django.core.signing import BadSignature, Signer
from oscar.apps.basket.models import Basket


def cart_data(request):
    """Return current cart data as JSON"""
    try:
        basket = None
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # For authenticated users, get their open basket
            try:
                basket = Basket.open.get(owner=request.user)
            except Basket.DoesNotExist:
                basket = None
        else:
            # For anonymous users, get basket from cookie (like Oscar middleware does)
            cookie_key = getattr(settings, 'OSCAR_BASKET_COOKIE_OPEN', 'oscar_open_basket')
            basket_hash = request.COOKIES.get(cookie_key)
            
            if basket_hash:
                try:
                    basket_id = Signer().unsign(basket_hash)
                    basket = Basket.open.get(pk=basket_id, owner=None)
                except (BadSignature, Basket.DoesNotExist):
                    basket = None
        
        if basket and basket.num_items > 0:
            return JsonResponse({
                'num_items': basket.num_items,
                'total_incl_tax': str(basket.total_incl_tax),
                'total_excl_tax': str(basket.total_excl_tax),
            })
        else:
            return JsonResponse({
                'num_items': 0,
                'total_incl_tax': '0.00',
                'total_excl_tax': '0.00',
            })
    except Exception as e:
        # Fallback for any errors
        return JsonResponse({
            'num_items': 0,
            'total_incl_tax': '0.00',
            'total_excl_tax': '0.00',
        })
