from django.conf import settings
from django.db import models

# Create your models here.

class UserCheckout(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) # not required
	email = models.EmailField(unique=True)


	def __str__(self):
		return self.email

# first arg in tuple is to be stored in database, second arg is to be displayed
ADDRESS_TYPE = (
	('billing', 'Billing'),
	('shipping', 'Shipping'), 
)

class UserAddress(models.Model):
	user = models.ForeignKey(UserCheckout)
	type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
	street = models.CharField(max_length=120)
	city = models.CharField(max_length=120)
	state = models.CharField(max_length=120)
	zipcode = models.CharField(max_length=120)

	def __str__(self):
		return self.street 

# class Order(models.Model):
# 	#cart
# 	#user checkout --> required
# 	#guest not required
# 	#shipping address
# 	#billing address
# 	#shipping total price
# 	#order total (cart total + shipping)
# 	#order_id --> custom id