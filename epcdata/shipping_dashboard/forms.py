"""
Minimal shipping dashboard forms to avoid model conflicts
"""
from django import forms


class WeightBasedForm(forms.Form):
    """
    Dummy form to prevent import errors - we don't actually use weight-based forms in dashboard
    """
    pass


class WeightBandForm(forms.Form):
    """
    Dummy form to prevent import errors - we don't actually use weight band forms in dashboard
    """
    pass
