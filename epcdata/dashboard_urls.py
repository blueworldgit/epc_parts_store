from django.urls import path
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view that uses Oscar's template but provides missing URLs"""
    login_url = '/accounts/login/'
    
    def get(self, request):
        # Try to import and use Oscar's IndexView
        try:
            from oscar.apps.dashboard.views import IndexView
            view = IndexView.as_view()
            return view(request)
        except Exception as e:
            # Show detailed error information
            import traceback
            error_details = traceback.format_exc()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Oscar Dashboard Debug</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .error {{ background: #fee; padding: 15px; border: 1px solid #fcc; margin: 20px 0; white-space: pre-wrap; font-family: monospace; font-size: 12px; overflow-x: auto; }}
                    .nav {{ margin: 20px 0; }}
                    .nav a {{ display: inline-block; margin-right: 15px; padding: 8px 12px; background: #007cba; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <h1>Oscar Dashboard Debug</h1>
                <p><strong>Oscar IndexView failed to load. Error details:</strong></p>
                <div class="error">{error_details}</div>
                
                <div class="nav">
                    <a href="/admin/">Django Admin</a>
                    <a href="/admin/catalogue/product/">Products</a>
                    <a href="/admin/partner/stockrecord/">Stock Records</a>
                    <a href="/">Store Front</a>
                </div>
                
                <h2>Available Management Links</h2>
                <ul>
                    <li><a href="/admin/catalogue/product/">Products (1,601 items)</a></li>
                    <li><a href="/admin/partner/stockrecord/">Stock Records (1,448 items)</a></li>
                    <li><a href="/admin/catalogue/category/">Categories</a></li>
                    <li><a href="/admin/partner/partner/">Partners</a></li>
                    <li><a href="/admin/order/order/">Orders</a></li>
                </ul>
            </body>
            </html>
            """
            return HttpResponse(html)

class SummaryView(LoginRequiredMixin, TemplateView):
    """Simple summary view placeholder"""
    login_url = '/accounts/login/'
    
    def get(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard Summary</title></head>
        <body>
            <h1>Dashboard Summary</h1>
            <p>Summary placeholder - this is where Oscar dashboard statistics would go.</p>
            <a href="/dashboard/">Back to Dashboard</a>
        </body>
        </html>
        """
        return HttpResponse(html)

app_name = 'dashboard'
urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('summary/', SummaryView.as_view(), name='summary'),
]
