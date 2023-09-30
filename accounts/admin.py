from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

# modifies the setting of the admin panel
class AccountAdmin(UserAdmin):
    # displays more than the default fields
    list_display = ('email','first_name','last_name','username','last_login', 'date_joined','is_active')
    list_display_links = ('email','first_name','last_name')
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',)


    # these lines 11-13 are needed because we have custom table and fields.
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account,AccountAdmin)