from django.contrib import admin
from . models import Product, Collection, Customer,Order, Promotion
admin.site.register(Product)
admin.site.register(Collection)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Promotion)