"""
Payment forms for Worldpay integration
"""
from django import forms
from django.utils.translation import gettext_lazy as _


class WorldpayPaymentDetailsForm(forms.Form):
    """
    Form for collecting payment method selection in checkout
    Updated to use Gateway API for direct payment processing
    """
    PAYMENT_CHOICES = [
        ('worldpay-gateway', _('Credit/Debit Card (Secure Processing)')),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_('Payment Method'),
        initial='worldpay-gateway'  # Default to Gateway API
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget.attrs.update({
            'class': 'form-check-input'
        })
