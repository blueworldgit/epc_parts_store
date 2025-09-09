"""
Phone number validation override using comprehensive monkey patching
"""
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class PhoneNumberPatchConfig(AppConfig):
    """
    App config that completely disables phone number validation on startup
    """
    name = 'phone_patch'
    label = 'phone_patch'
    
    def ready(self):
        """
        Comprehensive monkey patch to disable all phone number validation
        """
        try:
            # Import Django forms and Oscar modules
            from django import forms
            from django.core import validators
            import oscar.apps.address.forms
            import oscar.apps.checkout.forms
            
            # Patch django-phonenumber-field validation if it exists
            try:
                from phonenumber_field import formfields
                
                # Replace PhoneNumberField's clean method to accept anything
                def patched_clean(self, value):
                    if value in self.empty_values:
                        return ''
                    # Return the value as-is without any validation
                    return str(value) if value else ''
                
                formfields.PhoneNumberField.clean = patched_clean
                logger.info("Patched PhoneNumberField.clean method")
                
                # Also patch the widget
                from phonenumber_field import widgets
                widgets.PhoneNumberPrefixWidget.clean = lambda self, value: value
                
            except ImportError:
                logger.info("django-phonenumber-field not found, skipping that patch")
            
            # Patch at the model field level
            try:
                from phonenumber_field.modelfields import PhoneNumberField as ModelPhoneField
                
                def patched_model_clean(self, value, model_instance):
                    # Skip all validation, just return the value
                    return value
                
                def patched_validate(self, value, model_instance):
                    # Skip all validation
                    pass
                
                ModelPhoneField.clean = patched_model_clean
                ModelPhoneField.validate = patched_validate
                logger.info("Patched model PhoneNumberField validation")
                
            except ImportError:
                logger.info("Model PhoneNumberField not found")
            
            # Create a completely validation-free phone field
            def create_simple_phone_field():
                field = forms.CharField(
                    max_length=32,
                    required=False,
                    label='Phone number',
                    help_text='',
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Enter any phone number',
                        'pattern': '.*',  # Accept any pattern
                        'novalidate': True
                    })
                )
                field.validators = []  # Remove all validators
                return field
            
            # Patch UserAddressForm if it exists
            if hasattr(oscar.apps.address.forms, 'UserAddressForm'):
                UserAddressForm = oscar.apps.address.forms.UserAddressForm
                
                # Replace the field completely
                UserAddressForm.declared_fields['phone_number'] = create_simple_phone_field()
                
                # Patch the clean method
                def clean_phone_number(self):
                    value = self.cleaned_data.get('phone_number', '')
                    # Return whatever was entered, no validation
                    return str(value) if value else ''
                
                UserAddressForm.clean_phone_number = clean_phone_number
                logger.info("Patched UserAddressForm")
            
            # Also patch any base address form
            if hasattr(oscar.apps.address.forms, 'AbstractAddressForm'):
                AbstractAddressForm = oscar.apps.address.forms.AbstractAddressForm
                
                def clean_phone_number(self):
                    value = self.cleaned_data.get('phone_number', '')
                    return str(value) if value else ''
                
                AbstractAddressForm.clean_phone_number = clean_phone_number
                logger.info("Patched AbstractAddressForm")
            
            # Patch checkout forms as well
            if hasattr(oscar.apps.checkout.forms, 'ShippingAddressForm'):
                ShippingAddressForm = oscar.apps.checkout.forms.ShippingAddressForm
                
                def clean_phone_number(self):
                    value = self.cleaned_data.get('phone_number', '')
                    return str(value) if value else ''
                
                ShippingAddressForm.clean_phone_number = clean_phone_number
                logger.info("Patched checkout ShippingAddressForm")
            
            logger.info("Successfully applied comprehensive phone number validation patches")
            
        except Exception as e:
            logger.error(f"Error applying phone number patches: {e}")
            import traceback
            traceback.print_exc()
