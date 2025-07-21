from django.urls import path
from django.http import HttpResponse
from django.views.generic import View

class SimpleView(View):
    def get(self, request):
        return HttpResponse("<h1>Simple Dashboard Test</h1><p>This works!</p>")

app_name = 'dashboard'
urlpatterns = [
    path('', SimpleView.as_view(), name='index'),
]
