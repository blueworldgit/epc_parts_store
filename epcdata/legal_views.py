from django.shortcuts import render
from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    """Privacy Policy page view"""
    template_name = 'oscar/pages/privacy-policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Privacy Policy'
        return context


class DataProtectionPolicyView(TemplateView):
    """GDPR Data Protection Policy page view"""
    template_name = 'oscar/pages/data-protection-policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'GDPR Data Protection Policy'
        return context


class TermsAndConditionsView(TemplateView):
    """Terms and Conditions page view"""
    template_name = 'oscar/pages/terms-and-conditions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Terms and Conditions'
        return context


# Function-based views for convenience
def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'oscar/pages/privacy-policy.html', {
        'page_title': 'Privacy Policy'
    })


def data_protection_policy(request):
    """GDPR Data Protection Policy page"""
    return render(request, 'oscar/pages/data-protection-policy.html', {
        'page_title': 'GDPR Data Protection Policy'
    })


def terms_and_conditions(request):
    """Terms and Conditions page"""
    return render(request, 'oscar/pages/terms-and-conditions.html', {
        'page_title': 'Terms and Conditions'
    })
