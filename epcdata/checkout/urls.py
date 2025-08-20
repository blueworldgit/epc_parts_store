from django.urls import path
from . import views
from oscar.apps.checkout.views import (
    IndexView, ShippingAddressView, UserAddressUpdateView,
    UserAddressDeleteView, ShippingMethodView, PaymentMethodView,
    PreviewView, ThankYouView, PaymentDetailsView as OscarPaymentDetailsView
)

app_name = 'checkout'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    
    # Shipping address views
    path('shipping-address/', ShippingAddressView.as_view(), name='shipping-address'),
    path('user-address/edit/<int:pk>/', UserAddressUpdateView.as_view(), name='user-address-update'),
    path('user-address/delete/<int:pk>/', UserAddressDeleteView.as_view(), name='user-address-delete'),
    
    # Shipping method
    path('shipping-method/', ShippingMethodView.as_view(), name='shipping-method'),
    
    # Payment method
    path('payment-method/', PaymentMethodView.as_view(), name='payment-method'),
    
    # Custom payment details view (overrides Oscar's)
    path('payment-details/', views.PaymentDetailsView.as_view(), name='payment-details'),
    
    # Preview and thank you
    path('preview/', PreviewView.as_view(), name='preview'),
    path('thank-you/', ThankYouView.as_view(), name='thank-you'),
]
