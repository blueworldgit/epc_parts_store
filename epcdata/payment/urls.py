from django.urls import path
from . import views

urlpatterns = [
    path('worldpay/redirect/', views.WorldpayRedirectView.as_view(), name='worldpay-redirect'),
    path('worldpay/callback/', views.WorldpayCallbackView.as_view(), name='worldpay-callback'),
    path('worldpay/success/', views.WorldpaySuccessView.as_view(), name='worldpay-success'),
    path('worldpay/failure/', views.WorldpayFailureView.as_view(), name='worldpay-failure'),
    path('worldpay/cancel/', views.WorldpayCancelView.as_view(), name='worldpay-cancel'),
]
