from django.contrib import admin

# Register your models here.
from .models import UserCheckout, UserAddress, Order


class UserCheckoutAdmin(admin.ModelAdmin):
	list_display = ["id", "__str__"]
	class Meta:
		model = UserCheckout

admin.site.register(UserCheckout, UserCheckoutAdmin)

admin.site.register(UserAddress)

admin.site.register(Order)