from django.urls import path
import legal_views

app_name = 'legal'

urlpatterns = [
    path('privacy-policy/', legal_views.privacy_policy, name='privacy_policy'),
    path('data-protection-policy/', legal_views.data_protection_policy, name='data_protection_policy'),
    path('terms-and-conditions/', legal_views.terms_and_conditions, name='terms_conditions'),
]
