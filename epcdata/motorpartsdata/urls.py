from django.urls import path
from . import views

urlpatterns = [
    path('serial/', views.serial_lookup, name='serial_lookup'),
    path('parent/<int:parent_id>/', views.parent_detail, name='parent_detail'),
    path('child/<int:child_id>/', views.child_detail, name='child_detail'),
]
