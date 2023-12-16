from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

# shows the gallery of images for a product by merging the product table and product gallery table


# adds a product image thumbnail  in the admin panel
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1  # allows an extra field if the user needs more number of images

# displays fields on admin panel and populates the slug


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock',
                    'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    # mergest the ProductGallery model and the Product Model.
    inlines = [ProductGalleryInline]
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
admin.site.register(ProductGallery)
