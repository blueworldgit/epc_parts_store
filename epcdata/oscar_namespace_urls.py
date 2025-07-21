"""
Minimal Oscar namespace URLs for dashboard compatibility
This provides the basic URL namespaces that Oscar dashboard expects
"""
from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse

def placeholder_view(request):
    """Placeholder view for missing Oscar functionality"""
    return HttpResponse("""
    <h1>Oscar Feature Not Implemented</h1>
    <p>This feature requires full Oscar URL configuration.</p>
    <p><a href="/dashboard/">← Back to Dashboard</a></p>
    <p><a href="/admin/">Go to Admin</a></p>
    """)

def redirect_to_admin_login(request):
    """Redirect to Django admin login"""
    return redirect('/admin/login/')

def redirect_to_dashboard(request):
    """Redirect to dashboard"""
    return redirect('/dashboard/')

# Customer URLs (namespace: customer)
customer_urlpatterns = [
    path('', redirect_to_dashboard, name='summary'),  # Customer account summary
    path('profile/', placeholder_view, name='profile-view'),
    path('login/', redirect_to_admin_login, name='login'),
    path('logout/', redirect_to_admin_login, name='logout'),
    path('', placeholder_view, name='index'),
]

# Catalogue URLs (namespace: catalogue) 
catalogue_urlpatterns = [
    path('', placeholder_view, name='index'),
    path('products/', placeholder_view, name='detail'),
]

# Basket URLs (namespace: basket)
basket_urlpatterns = [
    path('', placeholder_view, name='summary'),
    path('add/', placeholder_view, name='add'),
]

# Checkout URLs (namespace: checkout)
checkout_urlpatterns = [
    path('', placeholder_view, name='index'),
    path('shipping/', placeholder_view, name='shipping-address'),
]
