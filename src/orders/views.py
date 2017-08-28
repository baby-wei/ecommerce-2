from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView

# Create your views here.
from .forms import AddressForm, UserAddressForm
from .models import UserAddress, UserCheckout


# create the form based on UserAddress model for guests and save the address detail for that specific checkout user
class UserAddressCreateView(CreateView):
	form_class = UserAddressForm
	template_name = "forms.html"
	success_url = "/checkout/address/"

	# (sub-function)
	def get_checkout_user(self):
		user_check_id = self.request.session.get("user_checkout_id")
		user_checkout = UserCheckout.objects.get(id=user_check_id)
		return user_checkout

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.get_checkout_user()
		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs) 


# get the radio select form of addresses for registered users and save the POST data as session variables
class AddressSelectFormView(FormView):
	form_class = AddressForm
	template_name = "orders/address_select.html"

	# (hidden-function to check if the user addresses are available)
	# if not, redirect to UserAddressCreateView
	def dispatch(self, *args, **kwargs):
		b_address, s_address = self.get_addresses()

		if b_address.count() == 0:
			messages.success(self.request, "Please add a billing address before continuing")
			return redirect("user_address_create")
		elif s_address.count() == 0:
			messages.success(self.request, "Please add a shipping address before continuing")
			return redirect("user_address_create")
		else:
			return super(AddressSelectFormView, self).dispatch(*args, **kwargs)


	# (sub-function)
	def get_addresses(self, *args, **kwargs):
		user_check_id = self.request.session.get("user_checkout_id")
		user_checkout = UserCheckout.objects.get(id=user_check_id)
		b_address = UserAddress.objects.filter(
				# this user is based of the UserCheckout
				user = user_checkout,
				type = 'billing',
			)
		s_address = UserAddress.objects.filter(
				# this user is based of the UserCheckout
				user = user_checkout,
				type = 'shipping',
			)
		return b_address, s_address


	def get_form(self, *args, **kwargs):
		form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
		b_address, s_address = self.get_addresses()

		form.fields["billing_address"].queryset = b_address
		form.fields["shipping_address"].queryset = s_address
		return form

	def form_valid(self, form, *args, **kwargs):
		billing_address = form.cleaned_data["billing_address"]
		shipping_address = form.cleaned_data["shipping_address"]

		self.request.session["billing_address_id"] = billing_address.id
		self.request.session["shipping_address_id"] = shipping_address.id

		return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs) 

	def get_success_url(self, *args, **kwargs):
		return "/checkout/"



