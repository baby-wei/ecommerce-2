from django.contrib import admin
from .models import Product, Variation, ProductImage
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
	list_display = ["id", "__str__"]

class VariationAdmin(admin.ModelAdmin):
	list_display = ["id", "product", "__str__"]

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductImage)