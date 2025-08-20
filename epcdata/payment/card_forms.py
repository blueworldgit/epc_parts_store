"""
Payment forms for Worldpay Gateway API integration
"""
from django import forms
from django.utils.translation import gettext_lazy as _
import re


class WorldpayPaymentDetailsForm(forms.Form):
    """
    Form for collecting payment method selection in checkout
    """
    PAYMENT_CHOICES = [
        ('worldpay-gateway', _('Credit/Debit Card (Secure Processing)')),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_('Payment Method'),
        initial='worldpay-gateway'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget.attrs.update({
            'class': 'form-check-input'
        })


class WorldpayCardDetailsForm(forms.Form):
    """
    Form for collecting card details for direct payment processing
    """
    cardholder_name = forms.CharField(
        max_length=100,
        label=_('Cardholder Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Smith',
            'autocomplete': 'cc-name'
        })
    )
    
    card_number = forms.CharField(
        max_length=19,
        label=_('Card Number'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'autocomplete': 'cc-number',
            'data-card-number': 'true'
        })
    )
    
    expiry_month = forms.ChoiceField(
        choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)],
        label=_('Expiry Month'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'autocomplete': 'cc-exp-month'
        })
    )
    
    expiry_year = forms.ChoiceField(
        label=_('Expiry Year'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'autocomplete': 'cc-exp-year'
        })
    )
    
    cvc = forms.CharField(
        max_length=4,
        label=_('Security Code (CVC)'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'autocomplete': 'cc-csc',
            'maxlength': '4'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate year choices (current year + 20 years)
        import datetime
        current_year = datetime.datetime.now().year
        year_choices = [(str(year), str(year)) for year in range(current_year, current_year + 21)]
        self.fields['expiry_year'].choices = year_choices
    
    def clean_card_number(self):
        """
        Validate and clean card number
        """
        card_number = self.cleaned_data.get('card_number', '')
        
        # Remove spaces and non-digits
        card_number = re.sub(r'\D', '', card_number)
        
        # Check length (13-19 digits for most cards)
        if len(card_number) < 13 or len(card_number) > 19:
            raise forms.ValidationError(_('Please enter a valid card number'))
        
        # Basic Luhn algorithm check
        if not self._luhn_check(card_number):
            raise forms.ValidationError(_('Please enter a valid card number'))
        
        return card_number
    
    def clean_cvc(self):
        """
        Validate CVC
        """
        cvc = self.cleaned_data.get('cvc', '')
        
        # Remove non-digits
        cvc = re.sub(r'\D', '', cvc)
        
        # Check length (3 or 4 digits)
        if len(cvc) not in [3, 4]:
            raise forms.ValidationError(_('Please enter a valid security code'))
        
        return cvc
    
    def clean(self):
        """
        Validate the entire form
        """
        cleaned_data = super().clean()
        
        # Check if expiry date is in the future
        expiry_month = cleaned_data.get('expiry_month')
        expiry_year = cleaned_data.get('expiry_year')
        
        if expiry_month and expiry_year:
            import datetime
            current_date = datetime.datetime.now()
            expiry_date = datetime.datetime(int(expiry_year), int(expiry_month), 1)
            
            if expiry_date < current_date.replace(day=1):
                raise forms.ValidationError(_('Please enter a valid expiry date'))
        
        return cleaned_data
    
    def _luhn_check(self, card_number):
        """
        Perform Luhn algorithm check for card number validation
        """
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10 == 0
