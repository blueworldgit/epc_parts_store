"""
Minimal shipping dashboard views to avoid model conflicts
"""
from django.http import Http404
from django.views.generic import ListView


class WeightBasedCreateView(ListView):
    """
    Dummy view - we don't actually manage weight-based methods through dashboard
    """
    template_name = 'oscar/dashboard/shipping/weight_based_list.html'
    
    def get_queryset(self):
        return []


class WeightBasedUpdateView(ListView):
    """
    Dummy view - we don't actually manage weight-based methods through dashboard
    """
    template_name = 'oscar/dashboard/shipping/weight_based_list.html'
    
    def get_queryset(self):
        return []


class WeightBasedDeleteView(ListView):
    """
    Dummy view - we don't actually manage weight-based methods through dashboard
    """
    template_name = 'oscar/dashboard/shipping/weight_based_list.html'
    
    def get_queryset(self):
        return []


class WeightBasedListView(ListView):
    """
    Dummy view - we don't actually manage weight-based methods through dashboard
    """
    template_name = 'oscar/dashboard/shipping/weight_based_list.html'
    
    def get_queryset(self):
        return []
