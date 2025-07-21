from django.urls import path
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'oscar/dashboard/index.html'
    login_url = '/accounts/login/'

class SummaryView(View):
    def get(self, request):
        return HttpResponse("<h1>Summary</h1><p><a href='/dashboard/'>Back to Dashboard</a></p>")

class ReportsView(View):
    def get(self, request):
        return HttpResponse("<h1>Reports</h1><p><a href='/dashboard/'>Back to Dashboard</a></p>")

class StatisticsView(View):
    def get(self, request):
        return HttpResponse("<h1>Statistics</h1><p><a href='/dashboard/'>Back to Dashboard</a></p>")

class LogoutView(View):
    def get(self, request):
        from django.contrib.auth import logout
        logout(request)
        return HttpResponse("""
        <h1>Logged Out</h1>
        <p>You have been successfully logged out.</p>
        <p><a href='/accounts/login/'>Log in again</a> | <a href='/'>Home</a></p>
        """)

class CatalogueProductListView(View):
    def get(self, request):
        from django.shortcuts import redirect
        return redirect('/admin/catalogue/product/')

class OrderListView(View):
    def get(self, request):
        from django.shortcuts import redirect
        return redirect('/admin/order/order/')

class PartnerListView(View):
    def get(self, request):
        from django.shortcuts import redirect
        return redirect('/admin/partner/partner/')

app_name = 'dashboard'
urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('summary/', SummaryView.as_view(), name='summary'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('stats/', StatisticsView.as_view(), name='stats'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Catalogue URLs
    path('catalogue/products/', CatalogueProductListView.as_view(), name='catalogue-product-list'),
    path('catalogue/', CatalogueProductListView.as_view(), name='catalogue-list'),
    
    # Order URLs
    path('orders/', OrderListView.as_view(), name='order-list'),
    
    # Partner URLs  
    path('partners/', PartnerListView.as_view(), name='partner-list'),
]
