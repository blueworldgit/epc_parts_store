import oscar.apps.dashboard.shipping.apps as apps
from django.views.generic import TemplateView


class DummyView(TemplateView):
    """Dummy view to prevent AttributeError"""
    template_name = 'oscar/dashboard/shipping/dummy.html'


class ShippingDashboardConfig(apps.ShippingDashboardConfig):
    name = 'shipping_dashboard'
    label = 'shipping_dashboard'  # Use the same label as Oscar's shipping dashboard
    
    def ready(self):
        # Don't call super().ready() to avoid loading problematic Oscar forms/views
        # that depend on WeightBased models we don't have
        # But provide the necessary attributes that get_urls() expects
        self.weight_method_list_view = DummyView
        self.weight_method_create_view = DummyView
        self.weight_method_update_view = DummyView
        self.weight_method_edit_view = DummyView  # Add missing attribute
        self.weight_method_delete_view = DummyView
        self.weight_method_detail_view = DummyView
        self.weight_band_list_view = DummyView
        self.weight_band_create_view = DummyView
        self.weight_band_update_view = DummyView
        self.weight_band_edit_view = DummyView  # Add missing attribute
        self.weight_band_delete_view = DummyView
        self.order_and_item_list_view = DummyView
        self.order_and_item_create_view = DummyView
        self.order_and_item_update_view = DummyView
        self.order_and_item_edit_view = DummyView  # Add missing attribute
        self.order_and_item_delete_view = DummyView
