from django.urls import path
from django.http import HttpResponse
from django.views.generic import View

class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Oscar Dashboard</title></head>
        <body>
            <h1>Oscar Dashboard</h1>
            <p>Dashboard is working!</p>
            <ul>
                <li><a href="/admin/">Django Admin</a></li>
                <li><a href="/admin/catalogue/product/">Products</a></li>
                <li><a href="/admin/partner/stockrecord/">Stock Records</a></li>
            </ul>
        </body>
        </html>
        """
        return HttpResponse(html)

app_name = 'dashboard'
urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
]
