# Maxus Parts Direct Header - Django Oscar Integration

This package contains a complete header template that duplicates the design and functionality from your parent site (maxuspartsdirect.co.uk) for use with Django Oscar.

## Files Included

1. **header-clean.html** - Standalone HTML template for testing
2. **header-django-oscar.html** - Django Oscar template with proper template tags
3. **header-styles-clean.css** - Complete CSS styling matching parent site
4. **header-functionality.js** - JavaScript for interactive features
5. **README.md** - This integration guide

## Integration Steps

### 1. Copy Files to Django Project

```bash
# Copy template file
cp header-django-oscar.html /path/to/your/django/project/templates/oscar/partials/nav_primary.html

# Copy CSS file
cp header-styles-clean.css /path/to/your/django/project/static/css/header.css

# Copy JavaScript file  
cp header-functionality.js /path/to/your/django/project/static/js/header.js
```

### 2. Download Required Images

Download these images from your parent site and place them in your static files:

```bash
# Create images directory
mkdir -p /path/to/your/django/project/static/img/

# Download main logo
wget https://maxuspartsdirect.co.uk/wp-content/uploads/2023/11/Maxus-parts-logo-web.png -O static/img/maxus-parts-logo-web.png

# Download header extra badge
wget https://maxuspartsdirect.co.uk/wp-content/uploads/2025/08/new-man-parts-direct-logo-site-scaled.png -O static/img/new-man-parts-direct-logo-site-scaled.png

# Download man parts logo
wget https://maxuspartsdirect.co.uk/wp-content/uploads/2025/08/new-man-parts-direct-logo-site-1024x512.png -O static/img/new-man-parts-direct-logo-site-1024x512.png
```

### 3. Update Base Template

In your base template (usually `base.html` or `layout.html`), include the CSS and JavaScript:

```html
<!-- In the <head> section -->
<link rel="stylesheet" href="{% static 'css/header.css' %}">

<!-- Google Fonts (matching parent site) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,600;0,800;1,400;1,800&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&display=swap" rel="stylesheet">

<!-- Before closing </body> tag -->
<script src="{% static 'js/header.js' %}"></script>
```

### 4. Override Oscar Templates

Create these template overrides in your project:

#### templates/oscar/layout.html
```html
{% extends 'oscar/layout.html' %}
{% load static %}

{% block header %}
    {% include 'oscar/partials/nav_primary.html' %}
{% endblock %}

{% block extra_head %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'css/header.css' %}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,600;0,800;1,400;1,800&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&display=swap" rel="stylesheet">
{% endblock %}

{% block extra_js %}
    {{ block.super }}
    <script src="{% static 'js/header.js' %}"></script>
{% endblock %}
```

### 5. Custom Template Tags (Optional)

Create a custom template tag for basket quantity display:

#### templatetags/basket_tags.py
```python
from django import template
from oscar.apps.basket import utils

register = template.Library()

@register.inclusion_tag('oscar/partials/basket_quantity.html', takes_context=True)
def basket_quantity(context):
    request = context['request']
    basket = utils.get_basket(request)
    return {
        'basket': basket,
        'quantity': basket.num_items if basket else 0
    }

@register.inclusion_tag('oscar/partials/basket_display.html', takes_context=True)  
def basket_display(context):
    request = context['request']
    basket = utils.get_basket(request)
    return {
        'basket': basket,
        'request': request
    }
```

#### templates/oscar/partials/basket_quantity.html
```html
<span class="cart-count" {% if quantity == 0 %}style="display: none;"{% endif %}>
    {{ quantity }}
</span>
```

#### templates/oscar/partials/basket_display.html
```html
<!-- This template handles the cart sidebar content -->
{% if basket.num_items > 0 %}
    <div class="basket-items">
        {% for line in basket.lines.all %}
            <div class="basket-item">
                <span class="item-title">{{ line.product.title }}</span>
                <span class="item-quantity">{{ line.quantity }}</span>
                <span class="item-price">{{ line.line_price_incl_tax|currency }}</span>
            </div>
        {% endfor %}
    </div>
    <div class="basket-total">
        <strong>{% trans 'Total' %}: {{ basket.total_incl_tax|currency }}</strong>
    </div>
{% endif %}
```

### 6. URL Configuration

Ensure these URLs are configured in your Oscar project:

```python
# urls.py
from django.urls import path, include
from oscar.apps.search import urls as search_urls

urlpatterns = [
    path('', include('oscar.urls')),
    path('search/', include(search_urls)),
    # ... other URLs
]
```

### 7. Settings Configuration

Add these settings to your Django settings:

```python
# settings.py

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Oscar settings
OSCAR_SHOP_NAME = 'Maxus Parts Direct'
OSCAR_SHOP_TAGLINE = 'Quality Parts for Your Vehicle'

# Template context processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.core.context_processors.metadata',
                'oscar.apps.basket.context_processors.basket',
            ],
        },
    },
]
```

## Customization Options

### 1. Navigation Menu Items

Edit the navigation in `header-django-oscar.html`:

```html
<ul id="main-nav" class="main-nav tf_clearfix tf_box">
    <!-- Add/remove menu items here -->
    <li class="menu-item">
        <a href="{% url 'catalogue:category' category_slug='new-category' %}">New Category</a>
    </li>
</ul>
```

### 2. Logo and Branding

Replace the logo images with your own:

```html
<!-- Main logo -->
<img src="{% static 'img/your-logo.png' %}" alt="Your Brand">

<!-- Header badge -->  
<img src="{% static 'img/your-badge.png' %}" alt="Your Badge">
```

### 3. Colors and Styling

Modify the CSS variables in `header-styles-clean.css`:

```css
:root {
    --primary-color: #ff6b35;
    --primary-hover: #e55a2b;
    --text-color: #333;
    --background-color: #fff;
}
```

### 4. Mobile Responsiveness

The header is fully responsive and includes:
- Mobile-first design
- Touch-friendly navigation
- Collapsible menu
- Slide-out cart
- Search overlay

## Features Included

✅ **Exact Visual Match** - Matches parent site design  
✅ **Mobile Responsive** - Works on all devices  
✅ **Django Oscar Integration** - Uses proper template tags  
✅ **Search Functionality** - Integrated with Oscar search  
✅ **Basket Integration** - Shows cart quantity and items  
✅ **User Authentication** - Login/logout states  
✅ **Accessibility** - Screen reader support  
✅ **SEO Friendly** - Proper semantic HTML  
✅ **Fast Loading** - Optimized CSS and JS  

## Testing

1. **Standalone Testing**: Open `header-clean.html` in a browser to test the design
2. **Django Testing**: Run your Django development server and verify all links work
3. **Mobile Testing**: Test on various screen sizes
4. **Basket Testing**: Add items to cart and verify quantity updates

## Browser Compatibility

- Chrome 60+
- Firefox 55+  
- Safari 11+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Notes

- All CSS is optimized and minified
- JavaScript uses modern ES6 but is compatible with older browsers
- Images should be optimized before deployment
- Consider using a CDN for static files in production

## Troubleshooting

### Common Issues:

1. **CSS not loading**: Check STATIC_URL and static files configuration
2. **Images not showing**: Verify image paths in static files
3. **Template tags not working**: Ensure Oscar apps are in INSTALLED_APPS
4. **JavaScript errors**: Check browser console for specific errors

### Debug Steps:

```bash
# Collect static files
python manage.py collectstatic

# Check template syntax
python manage.py check

# Test URLs
python manage.py show_urls | grep -E "(basket|search|customer)"
```

## Support

For issues with Django Oscar integration, refer to:
- [Django Oscar Documentation](https://django-oscar.readthedocs.io/)
- [Django Oscar GitHub](https://github.com/django-oscar/django-oscar)

## License

This header template is designed specifically for Maxus Parts Direct and should match the licensing terms of your parent site.
