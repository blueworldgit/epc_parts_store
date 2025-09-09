from django.contrib import admin
from oscar.apps.catalogue.models import ProductAttributeValue, ProductAttribute, Product

# Create a proxy model for weight-specific admin
class WeightAttributeValue(ProductAttributeValue):
    class Meta:
        proxy = True
        verbose_name = "Product Weight"
        verbose_name_plural = "Product Weights"

# Custom admin for weight management
class WeightAdmin(admin.ModelAdmin):
    list_display = ['product', 'get_weight_value', 'get_product_price', 'get_stock_level']
    search_fields = ['product__title', 'product__upc']
    list_filter = ['product__categories']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show weight attributes
        try:
            weight_attr = ProductAttribute.objects.get(code='weight')
            return qs.filter(attribute=weight_attr)
        except ProductAttribute.DoesNotExist:
            return qs.none()
    
    def get_weight_value(self, obj):
        """Display the weight value"""
        return f"{obj.value_float:.2f} kg" if obj.value_float else "No weight"
    get_weight_value.short_description = "Weight"
    get_weight_value.admin_order_field = 'value_float'
    
    def get_product_price(self, obj):
        """Display the product's price for reference"""
        stock_record = obj.product.stockrecords.first()
        if stock_record and stock_record.price:
            return f"£{stock_record.price}"
        return "No price"
    get_product_price.short_description = "Product Price"
    get_product_price.admin_order_field = 'product__stockrecords__price'
    
    def get_stock_level(self, obj):
        """Display the stock level"""
        stock_record = obj.product.stockrecords.first()
        if stock_record:
            return stock_record.num_in_stock
        return "No stock record"
    get_stock_level.short_description = "Stock Level"
    
    def has_add_permission(self, request):
        """Don't allow adding through admin - use management command"""
        return False

# Register our proxy model with custom admin
admin.site.register(WeightAttributeValue, WeightAdmin)
