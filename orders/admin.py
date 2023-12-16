from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.

# adds the product variation together with the table Order


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    # make the fields uneditable as these are order details from the user
    readonly_fields = ('payment', 'user', 'product',
                       'quantity', 'product_price', 'ordered')
    extra = 0  # removes empty rows in the table

# controls the fields to display in the admin panel


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email',
                    'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name',
                     'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]  # shows the table for the order


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
