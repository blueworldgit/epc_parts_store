from django.urls import path
from . import views

urlpatterns = [
    path('serial/', views.serial_lookup, name='serial_lookup'),
    path('parent/<int:parent_id>/', views.parent_detail, name='parent_detail'),
    path('child/<int:child_id>/', views.child_detail, name='child_detail'),
    path('parts-pricing/<str:serial_number>/', views.parts_pricing_view, name='parts_pricing'),
    path('parts-pricing-debug/<str:serial_number>/', views.parts_pricing_debug, name='parts_pricing_debug'),
    path('part-detail/<str:part_number>/', views.part_pricing_detail, name='part_pricing_detail'),
]
