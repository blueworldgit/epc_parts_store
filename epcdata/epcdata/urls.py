from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('serial_lookup')),  # root redirects to /serial
    path('', include('motorpartsdata.urls')),  # This includes URLs from your parts app
]