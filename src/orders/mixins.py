from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from carts.models import Cart
from .models import Order 


class LoginRequiredMixin(object):
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class CartOrderMixin(object):
	# (sub-function) create or get new Order object and its id
	def get_order(self, *args, **kwargs):
		cart = self.get_cart()
		if cart is None:
			return None
		new_order_id = self.request.session.get("order_id")
		if new_order_id is None:
			new_order = Order.objects.create(cart=cart)
			self.request.session["order_id"] = new_order.id
		else:
			new_order = Order.objects.get(id=new_order_id)
		return new_order 

	#  (sub-function) get the Cart object
	def get_cart(self, *args, **kwargs):   
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			return None	
		cart = Cart.objects.get(id=cart_id)
		if cart.items.count() <= 0:
			return None
		return cart 


	# get_cart must return an obj or None
	# if you wanna do a redirect("cart"), do it outside this function with an 'if cart==None' call