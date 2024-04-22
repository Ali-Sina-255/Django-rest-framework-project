from django.contrib import admin
from .models import Product, Collection, Customer, Order, Promotion, Cart, CartItem


class AdminProduct(admin.ModelAdmin):
    prepopulated_fields = ({"slug": ("title",)})


admin.site.register(Product, AdminProduct)
admin.site.register(Collection)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Promotion)
admin.site.register(Cart)
admin.site.register(CartItem)
