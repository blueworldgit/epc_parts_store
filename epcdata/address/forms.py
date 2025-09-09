"""
Custom address forms to disable phone number validation
"""
from django import forms
from oscar.apps.address import forms as address_forms


class UserAddressForm(address_forms.UserAddressForm):
    """
    Custom user address form with disabled phone validation for all address management
    """
    
    # Override phone_number field with a simple CharField
    phone_number = forms.CharField(
        max_length=32,
        required=False,
        label='Phone number',
        help_text='',
        widget=forms.TextInput(attrs={'placeholder': 'Enter any phone number'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove validation requirements for phone number
        if 'phone_number' in self.fields:
            self.fields['phone_number'].required = False
            self.fields['phone_number'].validators = []  # Remove all validators
    
    def clean_phone_number(self):
        """
        Override phone number validation to accept any input
        """
        return self.cleaned_data.get('phone_number', '')
