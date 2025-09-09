"""
Custom forms for checkout to enforce UK-only shipping and disable phone validation
"""
from django import forms
from django.core.exceptions import ValidationError
from django_countries import countries
from oscar.apps.checkout import forms as checkout_forms
from oscar.apps.address.models import Country


class UKOnlyShippingAddressForm(checkout_forms.ShippingAddressForm):
    """
    Custom shipping address form that defaults to UK and completely disables phone validation
    """
    
    # Completely override phone_number field with a simple CharField
    phone_number = forms.CharField(
        max_length=32,
        required=False,
        label='Phone number',
        help_text='',
        widget=forms.TextInput(attrs={'placeholder': 'Enter any phone number'})
    )
    
    # Override country field to ensure it's always GB
    country = forms.ChoiceField(
        choices=[('GB', 'United Kingdom')],
        initial='GB',
        widget=forms.HiddenInput(),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Force country field setup
        self.fields['country'] = forms.ChoiceField(
            choices=[('GB', 'United Kingdom')],
            initial='GB',
            widget=forms.HiddenInput(),
            required=True
        )
        
        # Don't manipulate self.data to avoid CSRF token issues
        # Instead, rely on the initial value and clean() method
        
        # Remove validation requirements for a more relaxed checkout
        for field_name, field in self.fields.items():
            if field_name not in ['country']:  # Don't mess with country field
                field.required = False
                field.help_text = ""  # Remove all help text
                if field_name == 'phone_number':
                    field.validators = []  # Completely clear all validators
            
        # Make only essential fields required
        self.fields['line1'].required = True
        self.fields['line4'].required = True  # Town/City
        self.fields['postcode'].required = True
    
    def clean_country(self):
        """
        Always return GB as an Oscar Country instance for country field
        """
        from oscar.apps.address.models import Country
        return Country.objects.get(iso_3166_1_a2='GB')
    
    def clean_phone_number(self):
        """
        Override phone number validation to accept ANY input without any validation
        """
        phone_number = self.cleaned_data.get('phone_number', '')
        # Return whatever was entered, no validation at all
        return phone_number
    
    def clean(self):
        """
        Override clean method to disable most validation except essential fields
        """
        # Call parent clean to handle field processing
        try:
            cleaned_data = super().clean()
        except ValidationError:
            # If parent validation fails, start with basic data
            cleaned_data = {}
            for field_name, field in self.fields.items():
                if field_name in self.data:
                    cleaned_data[field_name] = self.data[field_name]
        
        # FORCE country to be GB - always, using proper Oscar Country instance
        from oscar.apps.address.models import Country
        cleaned_data['country'] = Country.objects.get(iso_3166_1_a2='GB')
        
        # Force phone_number to whatever was entered
        cleaned_data['phone_number'] = self.data.get('phone_number', '')
        
        # Clear all validation errors except for essential fields
        if hasattr(self, '_errors'):
            # Remove phone_number and country errors
            for field_to_clear in ['phone_number', 'country']:
                if field_to_clear in self._errors:
                    del self._errors[field_to_clear]
            
            # Keep only critical field errors
            essential_fields = ['line1', 'line4', 'postcode']
            errors_to_keep = {}
            for field in essential_fields:
                if field in self._errors:
                    errors_to_keep[field] = self._errors[field]
            self._errors = errors_to_keep
        
        # Manually validate only essential fields
        if not cleaned_data.get('line1', '').strip():
            self.add_error('line1', 'Address line 1 is required.')
        
        if not cleaned_data.get('line4', '').strip():  # Town/City
            self.add_error('line4', 'Town/City is required.')
        
        if not cleaned_data.get('postcode', '').strip():
            self.add_error('postcode', 'Postcode is required.')
        
        return cleaned_data
        
    class Meta(checkout_forms.ShippingAddressForm.Meta):
        pass
