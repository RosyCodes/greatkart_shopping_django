from django.contrib import admin
from .models import Product, Variation, ReviewRating


# displays fields on admin panel and populates the slug
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock',
                    'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

# displays all the product variation fields and allows is_active to be editable
# displays filter categories


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category',
                    'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
