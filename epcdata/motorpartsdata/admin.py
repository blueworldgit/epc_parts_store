from django.contrib import admin
from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import (
    SerialNumber, ParentTitle, ChildTitle, Part, PricingData,
    ShippingAddress, ShippingMethod
)

# Custom forms to ensure proper widgets
class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'
        widgets = {
            'country': CountrySelectWidget(),
        }

class ShippingMethodForm(forms.ModelForm):
    class Meta:
        model = ShippingMethod
        fields = '__all__'
        widgets = {
            'countries': CountrySelectWidget(attrs={'multiple': True}),
        }

# Register your models here.

@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    list_display = ['serial']
    search_fields = ['serial']

@admin.register(ParentTitle)
class ParentTitleAdmin(admin.ModelAdmin):
    list_display = ['title', 'serial_number']
    list_filter = ['serial_number']
    search_fields = ['title']

@admin.register(ChildTitle)
class ChildTitleAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent']
    list_filter = ['parent']
    search_fields = ['title']

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'usage_name', 'child_title', 'call_out_order']
    list_filter = ['child_title', 'lr']
    search_fields = ['part_number', 'usage_name']
    ordering = ['call_out_order']

@admin.register(PricingData)
class PricingDataAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'description', 'list_price', 'active']
    list_filter = ['active', 'vat_code']
    search_fields = ['part_number__part_number', 'description']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    form = ShippingAddressForm
    list_display = ['name', 'city', 'country', 'is_default', 'created_at']
    list_filter = ['country', 'is_default', 'created_at']
    search_fields = ['name', 'city', 'address_line_1']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
    )

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    form = ShippingMethodForm
    list_display = ['name', 'price', 'delivery_estimate', 'is_active', 'countries_display']
    list_filter = ['is_active', 'countries']
    search_fields = ['name', 'description']
    ordering = ['price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Coverage', {
            'fields': ('countries',)
        }),
        ('Pricing & Delivery', {
            'fields': ('price', 'estimated_days_min', 'estimated_days_max')
        }),
    )
    
    def countries_display(self, obj):
        return ", ".join([str(country) for country in obj.countries])
    countries_display.short_description = "Available Countries"
    
    def delivery_estimate(self, obj):
        return obj.delivery_estimate()
    delivery_estimate.short_description = "Delivery Time"
