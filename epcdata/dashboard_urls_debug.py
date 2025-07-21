from django.urls import path
from django.http import HttpResponse
from django.views.generic import View

class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
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

app_name = 'dashboard'
urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
]
