import braintree

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin
# Create your views here.
from orders.forms import GuestCheckoutForm
from orders.mixins import CartOrderMixin
from orders.models import UserCheckout, Order, UserAddress 
from products.models import Variation

from .models import Cart, CartItem




if settings.DEBUG:
	braintree.Configuration.configure(braintree.Environment.Sandbox,
      merchant_id=settings.BRAINTREE_MERCHANT_ID,
      public_key=settings.BRAINTREE_PUBLIC,
      private_key=settings.BRAINTREE_PRIVATE,
    )


class ItemCountView(View):
	def get(self, request, *ars, **kwargs):
		if request.is_ajax():
			cart_id = self.request.session.get("cart_id")

			if cart_id == None:
				count = 0
			else:
				cart = Cart.objects.get(id=cart_id)
				count = cart.items.count()
			request.session["cart_item_count"] = count 
			return JsonResponse({"count": count})
		else:
			raise Http404

class CartView(SingleObjectMixin, View):
	model = Cart
	template_name = "carts/view.html"

	def get_object(self, *args, **kwargs):
		# if user uses the cart, it ends the session when the browser is closed
		self.request.session.set_expiry(0)     

		# Setting a new session variable 'cart'
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			# Cart.objects.create()
			cart = Cart()
			#self.request.user.tax_percentage()
			cart.tax_percentage = 0.075
			cart.save()
			cart_id = cart.id 
			# create a new key for request.session and assign it with a value	
			self.request.session["cart_id"] = cart_id
		
		cart = Cart.objects.get(id=cart_id)
		if self.request.user.is_authenticated():
			cart.user = self.request.user
			cart.save()

		return cart 

	def get(self, request, *args, **kwargs):
		cart = self.get_object()

		# grab query on url and create cartitem accordingly
		item_id = request.GET.get("item")
		delete_item = request.GET.get("delete", False)
		flash_message = ""
		item_added = False
		if item_id:
			item_instance = get_object_or_404(Variation, id=item_id)
			# 2nd arg gives qty a default qty of 1
			qty = request.GET.get("qty", 1)
			try:
				if int(qty) < 1:
					delete_item = True
			except:
				raise Http404
			cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
			if created:
				flash_message = "Successfully added to cart."
				item_added = True
			if delete_item:
				flash_message = "Item removed successfully."
				cart_item.delete()
			else:
				if not created:
					flash_message = "Quantity has been updated successfully."
				cart_item.quantity = qty
				cart_item.save()
			if not request.is_ajax():
				return HttpResponseRedirect(reverse("cart"))
				# return cart_item.cart.get_absolute_url()

		if request.is_ajax():
			try:
				total = cart_item.line_item_total
			except:
				total = None
			try:
				subtotal = cart_item.cart.subtotal
			except:
				subtotal = None
			try:
				cart_total = cart_item.cart.total 
			except:
				cart_total = None
			try:
				tax_total = cart_item.cart.tax_total 
			except:
				tax_total = None
			try:
				total_items = cart_item.cart.items.count()
			except:
				total_items = 0
			data = {
					"deleted": delete_item, 
					"item_added": item_added,
					"line_total": total,
					"sub_total": subtotal,
					"cart_total": cart_total,
					"tax_total": tax_total,
					"flash_message": flash_message,
					"total_items": total_items,
					}
			return JsonResponse(data)


		context = {
			"object": self.get_object()
		}
		template = self.template_name
		return render(request, template, context)


"""
CheckoutView handles login page, order view
--redirects to select address page, add address page--
"""
class CheckoutView(CartOrderMixin, FormMixin, DetailView):
	model = Cart
	template_name = "carts/checkout_view.html"
	form_class = GuestCheckoutForm


	#  (sub-function) get the Cart object
	def get_object(self, *args, **kwargs):   
		cart = self.get_cart()
		if cart == None:
			return None	
		return cart 


	# handles logins
	def get_context_data(self, *args, **kwargs):
		context = super(CheckoutView, self).get_context_data(*args, **kwargs)
		

		# decides whether user_can_continue
		# displays either the login page or the order view
		user_can_continue = False
		user_check_id = self.request.session.get("user_checkout_id")

		if self.request.user.is_authenticated():	# REGISTERED USER
			user_can_continue = True
			# create a UserCheckout object for registered users
			user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
			user_checkout.user = self.request.user
			user_checkout.save()
			context['client_token'] = user_checkout.get_client_token()
			self.request.session["user_checkout_id"] = user_checkout.id 
		elif not self.request.user.is_authenticated() or user_check_id == None:
			context["login_form"] = AuthenticationForm()
			# redirects user back to the page he/she just request i.e. CheckoutView
			context["next_url"] = self.request.build_absolute_uri()
		else:
			pass

		if user_check_id != None:
			user_can_continue = True
			if not self.request.user.is_authenticated():	#GUEST USER
				user_checkout_2 = UserCheckout.objects.get(id=user_check_id)
				context['client_token'] = user_checkout_2.get_client_token()

		context["order"] = self.get_order()
		context["user_can_continue"] = user_can_continue
		# .get_form() method comes from FormMixin
		context["form"] = self.get_form()
		return context


	# handles post data for guests
	def post(self, request, *args, **kwargs):
		# object created just to prevent error
		self.object = self.get_object()
		
		# requires unregistered users to continue as Guests
		form = self.get_form()
		if form.is_valid():
			# create a UserCheckout object for guests
			email = form.cleaned_data.get("email")
			user_checkout, created = UserCheckout.objects.get_or_create(email=email)
			request.session["user_checkout_id"] = user_checkout.id 
			return self.form_valid(form)
		else:
			return self.form_invalid(form)


	def get_success_url(self):
		return reverse("checkout") 




	# creating a new order -- making sure all required informations are there
	# You will only hv a user_checkout_id after you login as guest or registered user
	def get(self, request, *args, **kwargs):
		get_data = super(CheckoutView, self).get(request, *args, **kwargs)
		cart = self.get_object()
		if cart == None:
			return redirect("cart")
		new_order = self.get_order()
		user_checkout_id = request.session.get('user_checkout_id')
		if user_checkout_id != None:
			user_checkout = UserCheckout.objects.get(id=user_checkout_id)
			# redirect guests/users to the add/select address page
			if new_order.billing_address == None or new_order.shipping_address == None:
				return redirect("order_address")

			new_order.user = user_checkout 
			new_order.save()
		return get_data 


class CheckoutFinalView(CartOrderMixin, View):
	def post(self, request, *args, **kwargs):
		# Real transaction process
		order = self.get_order()
		order_total = order.order_total
		nonce = request.POST.get("payment_method_nonce")
		if nonce:
			result = braintree.Transaction.sale({
			    "amount": order_total,
			    "payment_method_nonce": nonce,
			    "billing": {
				    "postal_code": "%s" %(order.billing_address.zipcode),
				},
			    "options": {
			        "submit_for_settlement": True
			    }
			})
			if result.is_success:		
				order.mark_completed(order_id = result.transaction.id )
				messages.success(request, "Thank you for your order.")
				del self.request.session["cart_id"]
				del self.request.session["order_id"]
			else:
				message.success(request, "%s" %(result.message))
				return redirect("checkout")


		# Mockup transaction process
		# order = self.get_order()
		# if request.POST.get("payment_token") == 'ABC':
		# 	order.mark_completed()
		# 	messages.success(request, "Thank you for your order.")
		# 	del self.request.session["cart_id"]
		# 	del self.request.session["order_id"]


		return redirect("order_detail", pk=order.pk)


	def get(self, request, *args, **kwargs):
		return redirect("checkout")