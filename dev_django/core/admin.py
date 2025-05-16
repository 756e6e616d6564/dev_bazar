from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Product, ProductCategory, Sale, SaleItem

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de usuario'

# Extender el modelo de usuario predeterminado
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleItemInline]
    list_display = ('id', 'seller', 'total_amount', 'created_at')
    search_fields = ('seller__username',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(Sale, SaleAdmin)
