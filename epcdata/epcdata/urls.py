from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template.response import TemplateResponse
from svg_views import svg_diagram_view
from django.apps import apps

def product_detail(request, pk, product_slug=None):
    """Simple product detail view"""
    try:
        from oscar.core.loading import get_model
        from motorpartsdata.models import Part, ChildTitle
        
        Product = get_model('catalogue', 'Product')
        product = get_object_or_404(Product, pk=pk)
        stock_record = product.stockrecords.first()
        price = f"£{stock_record.price}" if stock_record else "Price not set"
        
        # Try to get SVG diagram
        svg_section = ""
        try:
            part = Part.objects.get(part_number=product.upc)
            child_title = part.child_title
            if child_title and child_title.svg_code:
                svg_section = f"""
                <div style="margin-top: 30px; border: 1px solid #ddd; padding: 20px;">
                    <h3>Technical Diagram - {child_title.title}</h3>
                    <div style="border: 1px solid #ccc; padding: 10px; background: #f9f9f9; overflow: auto; max-height: 600px; text-align: center;">
                        {child_title.svg_code}
                    </div>
                </div>
                """
        except (Part.DoesNotExist, ChildTitle.DoesNotExist):
            pass
        
        html = f"""
        <html>
        <head><title>{product.title} - EPC Motor Parts Store</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .nav {{ background: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #0066cc; }}
            .product-detail {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
            svg {{ max-width: 100%; height: auto; }}
        </style>
        </head>
        <body>
            <div class="nav">
                <a href="/">← Back to Home</a>
                <a href="/admin/">Admin</a>
                <a href="/admin/catalogue/product/{product.pk}/change/">Edit Product</a>
            </div>
            
            <div class="product-detail">
                <h1>{product.title}</h1>
                <p><strong>UPC:</strong> {product.upc or 'Not set'}</p>
                <p><strong>Price:</strong> {price}</p>
                <p><strong>Description:</strong> {product.description or 'No description available'}</p>
                
                {f'<p><strong>Stock:</strong> {stock_record.num_in_stock} units</p>' if stock_record and stock_record.num_in_stock else ''}
                {f'<p><strong>Partner:</strong> {stock_record.partner.name}</p>' if stock_record and stock_record.partner else ''}
            </div>
            
            {svg_section}
        </body>
        </html>
        """
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"<h1>Product Not Found</h1><p>Error: {e}</p><p><a href='/'>Back to Home</a></p>")

def homepage(request):
    """Simple homepage that lists products"""
    try:
        from oscar.core.loading import get_model
        Product = get_model('catalogue', 'Product')
        StockRecord = get_model('partner', 'StockRecord')
        products = Product.objects.all()[:10]  # Show first 10 products
        
        html = f"""
        <html>
        <head><title>EPC Motor Parts Store</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .nav {{ background: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
            .nav a {{ margin-right: 20px; text-decoration: none; color: #0066cc; }}
            .product {{ margin: 10px 0; padding: 10px; border-left: 3px solid #0066cc; }}
        </style>
        </head>
        <body>
            <div class="nav">
                <h1>EPC Motor Parts Store</h1>
                <a href="/admin/">Django Admin</a>
                <a href="/dashboard/">Oscar Dashboard</a>
                <a href="/admin/catalogue/product/">Manage Products</a>
                <a href="/admin/partner/stockrecord/">Manage Pricing</a>
                <a href="/api/">API</a>
            </div>
            
            <h2>Welcome to your Oscar E-commerce Store!</h2>
            <p><strong>Total Products:</strong> {Product.objects.count()}</p>
            
            <h3>Recent Products:</h3>
        """
        
        for product in products:
            # Get price from stock record
            stock_record = product.stockrecords.first()
            price = f"£{stock_record.price}" if stock_record else "Price not set"
            html += f'<div class="product"><strong>{product.title}</strong> - {price}</div>'
        
        html += """
            <h3>Oscar Management Interfaces:</h3>
            <ul>
                <li><a href="/dashboard/">Oscar Dashboard</a> - Full e-commerce dashboard interface</li>
                <li><a href="/admin/catalogue/product/">Products</a> - Manage your product catalog</li>
                <li><a href="/admin/partner/stockrecord/">Stock & Pricing</a> - Manage inventory and prices</li>
                <li><a href="/admin/catalogue/category/">Categories</a> - Organize products</li>
                <li><a href="/admin/partner/partner/">Partners</a> - Manage suppliers</li>
                <li><a href="/admin/order/order/">Orders</a> - View customer orders</li>
            </ul>
        </body>
        </html>
        """
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"<h1>EPC Motor Parts Store</h1><p>Error loading products: {e}</p><p><a href='/admin/'>Admin Panel</a></p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('motorpartsdata.urls')),  # Your API endpoints under /api/
    
    # SVG diagram endpoint
    path('svg-diagram/<str:upc>/', svg_diagram_view, name='svg_diagram'),
    
    # Oscar URLs with proper app configuration for 3.2
    path('dashboard/', include((apps.get_app_config('dashboard').urls[0], apps.get_app_config('dashboard').name), namespace=apps.get_app_config('dashboard').namespace)),
    path('accounts/', include((apps.get_app_config('customer').urls[0], apps.get_app_config('customer').name), namespace=apps.get_app_config('customer').namespace)),
    path('basket/', include((apps.get_app_config('basket').urls[0], apps.get_app_config('basket').name), namespace=apps.get_app_config('basket').namespace)),
    path('checkout/', include((apps.get_app_config('checkout').urls[0], apps.get_app_config('checkout').name), namespace=apps.get_app_config('checkout').namespace)),
    path('catalogue/', include((apps.get_app_config('catalogue').urls[0], apps.get_app_config('catalogue').name), namespace=apps.get_app_config('catalogue').namespace)),
    path('search/', include((apps.get_app_config('search').urls[0], apps.get_app_config('search').name), namespace=apps.get_app_config('search').namespace)),
    path('offers/', include((apps.get_app_config('offer').urls[0], apps.get_app_config('offer').name), namespace=apps.get_app_config('offer').namespace)),
    path('wishlists/', include((apps.get_app_config('wishlists').urls[0], apps.get_app_config('wishlists').name), namespace=apps.get_app_config('wishlists').namespace)),
    
    # Product detail URLs with proper namespace for Oscar admin integration
    path('products/', include(([
        path('<slug:product_slug>-<int:pk>/', product_detail, name='detail'),
        path('<int:pk>/', product_detail, name='detail-simple'),  # Fallback for pk only
    ], 'products'), namespace='products')),
    
    # Alternative URL without namespace
    path('product/<int:pk>/', product_detail, name='product_detail'),
    
    # Move the current homepage to /backendstuff
    path('backendstuff/', homepage, name='backend_homepage'),
    
    # Redirect root to catalogue
    path('', lambda request: redirect('/catalogue/'), name='homepage'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)