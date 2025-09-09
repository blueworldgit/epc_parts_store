from django.http import JsonResponse
from django.views import View
from oscar.apps.catalogue.models import Category, Product

class CategoryProductCountView(View):
    def get(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
            
            # Get all descendant categories and include the current category
            descendant_categories = list(category.get_descendants()) + [category]
            
            # Count distinct products across all these categories
            product_count = Product.objects.filter(categories__in=descendant_categories).distinct().count()
            
            return JsonResponse({'count': product_count})
        except Category.DoesNotExist:
            return JsonResponse({'count': 0})
        except Exception as e:
            return JsonResponse({'count': 0, 'error': str(e)})
