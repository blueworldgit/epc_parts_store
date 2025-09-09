from oscar.apps.catalogue.views import CatalogueView
from oscar.apps.catalogue.models import Category, Product
from django.db.models import Q

class CustomCategoryView(CatalogueView):
    """
    Custom category view that includes product counts for child categories
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current category
        category = context.get('category')
        
        if category:
            # Get child categories with their product counts
            child_categories = category.get_children()
            child_categories_with_counts = []
            
            for child_category in child_categories:
                # Get all descendant categories including the child category itself
                descendant_categories = list(child_category.get_descendants()) + [child_category]
                
                # Count distinct products across all these categories
                product_count = Product.objects.filter(categories__in=descendant_categories).distinct().count()
                
                # Add the count as an attribute to the category object
                child_category.product_count = product_count
                child_categories_with_counts.append(child_category)
            
            context['child_categories_with_counts'] = child_categories_with_counts
        
        return context
