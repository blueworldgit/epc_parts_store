from django import forms
from django.utils.translation import gettext_lazy as _


class WorldpayRedirectForm(forms.Form):
    """
    Form for Worldpay Hosted Payment Page redirect
    """
    # Hidden fields that will be submitted to Worldpay
    instId = forms.CharField(widget=forms.HiddenInput())
    cartId = forms.CharField(widget=forms.HiddenInput())
    amount = forms.CharField(widget=forms.HiddenInput())
    currency = forms.CharField(widget=forms.HiddenInput())
    desc = forms.CharField(widget=forms.HiddenInput())
    testMode = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    # Customer details
    name = forms.CharField(
        max_length=100, 
        label=_("Cardholder Name"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address1 = forms.CharField(
        max_length=100, 
        label=_("Address Line 1"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address2 = forms.CharField(
        max_length=100, 
        label=_("Address Line 2"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    town = forms.CharField(
        max_length=50, 
        label=_("City"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    region = forms.CharField(
        max_length=50, 
        label=_("State/Region"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    postcode = forms.CharField(
        max_length=20, 
        label=_("Postal Code"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    country = forms.CharField(
        max_length=2, 
        label=_("Country"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel = forms.CharField(
        max_length=20, 
        label=_("Phone Number"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


class WorldpayPaymentDetailsForm(forms.Form):
    """
    Simple form to show payment method selection
    """
    payment_method = forms.ChoiceField(
        choices=[('worldpay', 'Credit/Debit Card via Worldpay')],
        widget=forms.RadioSelect(),
        initial='worldpay'
    )
