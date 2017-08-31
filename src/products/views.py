from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django_filters import FilterSet, CharFilter, NumberFilter
# Create your views here.

from .forms import VariationInventoryFormSet, ProductFilterForm
from .mixins import StaffRequiredMixin
from .models import Product, Variation, Category 


import random

class ProductDetailView(DetailView):
	model = Product 
	#template = "<appname>/<modelname>_<viewname>.html"
	#context = "object"

	# To overwrite default:
	# template_name = ...
	# def get_context_data(self): ...

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		instance = self.get_object()
		#order_by("?") = sorted(...random.random())
		# We don't use order_by becoz it conflicts with .distinct(), hey cannot be used 2geter
		context["related"] = sorted(self.model.objects.get_related(instance)[:6], 
			key=lambda x: random.random())

		return context

# Function-based view:
# def product_detail_view_func(request, id):
# 	#product_instance = Product.objects.get(id=id)
# 	product_instance = get_object_or_404(Product, id=id)
# 	try:
# 		product_instance = Product.objects.get(id=id)
# 	except Product.DoesNotExist:
# 		raise Http404
# 	except:
# 		raise Http404

# 	template = "products/product_detail.html"
# 	context = {
# 		"object": product_instance
# 	}
# 	return render(request, template, context)


class ProductFilter(FilterSet):
	title = CharFilter(name='title', lookup_expr='icontains', distinct=True)
	category = CharFilter(name='categories__title', lookup_expr='icontains', distinct=True)
	category_id = CharFilter(name='categories__id', lookup_expr='icontains', distinct=True)
	min_price = NumberFilter(name='variation__price', lookup_expr='gte', distinct=True) #(some_price__gte=somequery)
	max_price = NumberFilter(name='variation__price', lookup_expr='lte', distinct=True)
	class Meta:
		model = Product 
		fields = [			
			'description',
		]

# Function-based filter
# def product_list(request):
# 	qs = Product.objects.all()
# 	ordering = request.GET.get("ordering")
# 	if ordering:
# 		qs = Product.objects.all().order_by(ordering)
# 	f = ProductFilter(request.GET, queryset=qs)
# 	return render(request, "products/product_list.html", {"object_list": f})


class FilterMixin(object):
	filter_class = None
	search_ordering_param = "ordering"

	def get_queryset(self, *args, **kwargs):
		try:
			qs = super(FilterMixin, self).get_queryset(*args, **kwargs)
			return qs 
		except:
			raise ImproperlyConfigured("You must have a queryset in order to use the FilterMixin")

	def get_context_data(self, *args, **kwargs):
		context = super(FilterMixin, self).get_context_data(*args, **kwargs)
		qs = self.get_queryset()
		ordering = self.request.GET.get(self.search_ordering_param)
		if ordering:
			qs = qs.order_by(ordering)
		filter_class = self.filter_class
		if filter_class:
			f = filter_class(self.request.GET, queryset=qs)
			context["object_list"] = f 
		return context 


class ProductListView(FilterMixin, ListView):
	model = Product 
	queryset = Product.objects.all().active()
	filter_class = ProductFilter

	def get_context_data(self, *args, **kwargs):
		# get default context data dictionary
		context = super(ProductListView, self).get_context_data(*args, **kwargs)
		# overwrite default or create new key-value pairs
		context["filter_form"] = ProductFilterForm(data=self.request.GET or None)
		return context

	def get_queryset(self, *args, **kwargs):
		qs = super(ProductListView, self).get_queryset(*args, **kwargs)
		# if parameter 'q' doesn't exist, the function returns None
		query = self.request.GET.get("q")
		if query:
			# Standard lookup:
			#qs = self.model.objects.filter(title__icontains=query)
			# Complex lookup:
			qs = self.model.objects.filter(
				Q(title__icontains=query) |
				Q(description__icontains=query)
				)
			try:
				qs2 = self.model.objects.filter(
					Q(price=query)
				)
				qs = (qs | qs2).distinct()
			except:
				pass 
		return qs


class VariationListView(StaffRequiredMixin, ListView):
	model = Variation 
	queryset = Variation.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(VariationListView, self).get_context_data(*args, **kwargs)
		context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
		return context

	def get_queryset(self, *args, **kwargs):
		product_pk = self.kwargs.get("pk")
		if product_pk:
			product = get_object_or_404(Product, pk=product_pk)
			queryset = Variation.objects.filter(product=product)
		return queryset

	def post(self, request, *args, **kwargs):
		formset = VariationInventoryFormSet(request.POST, request.FILES)
		if formset.is_valid():
			formset.save(commit=False)
			for form in formset:
				new_item = form.save(commit=False)
				if new_item.title:
					product_pk = self.kwargs.get("pk")
					product = get_object_or_404(Product, pk=product_pk)
					new_item.product = product
					new_item.save()
				
			# django messages framework
			messages.success(request, "Your inventory and pricing has been updated")
			return redirect("products")
		raise Http404

class CategoryListView(ListView):
	model = Category 
	queryset = Category.objects.all()
	template_name = "products/product_list.html"

class CategoryDetailView(DetailView):
	model = Category 
	def get_context_data(self, *args, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
		obj = self.get_object()
		product_set = obj.product_set.all()
		default_products = obj.default_category.all()
		# combining two querysets
		products = (product_set | default_products).distinct()
		context['products'] = products
		return context