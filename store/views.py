from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, CheckoutAddress
from django.contrib import  messages
from django.views.generic import ListView, DetailView, View, CreateView
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm, NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User


# class Register_CreateView(CreateView):
#     model = User
#     form_class = NewUserForm
#     template_name = "store/register.html"

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'user'
#         return super().get_context_data(**kwargs)

#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         return redirect("home")


def register_request(request):

	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="store/register.html", context={"register_form":form})


def login_request(request):
   
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="store/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("index")

# Create your views here.
def index(request):
    return render(request, "store/base.html")

# Listing all the product
class HomeView(ListView):
    model = Item
    context_object_name = "items"
    template_name = "store/home.html"

# product details view
class ProductView(DetailView):
    model = Item
    context_object_name = "item"
    template_name = "store/details.html"


# Order summary of ordered product
class Order_summaryView(LoginRequiredMixin,  View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {"order":order,}
            return render(self.request, "store/order_summary.html", context )
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("product")

# add to cart
login_required()
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(user=request.user, item=item, ordered=False )
    order_query = Order.objects.filter(user = request.user, ordered = False)

    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__pk = item.pk).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request, f"Added another {order_item.item.item_name} to your cart ")
            return redirect("order_summary")
        else:
            order.items.add(order_item)
            messages.info(request, f"{order_item.item.item_name } is added to your cart")
            return redirect("order_summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, f"{order_item.item.item_name } is added to your cart")
        return redirect("order_summary" )

# remove from cart
login_required()
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_query = Order.objects.filter(user = request.user, ordered = False)

    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(user=request.user, item=item, ordered=False)[0]
            order_item.delete()
            messages.info(request, f"{order_item.item.item_name } is removed from your cart")
            return redirect("order_summary")
        else:
            messages.info(request, f"{item.item_name } is not in your cart")
            return redirect("product", pk=pk)
    else:
        messages.info(request, "You do not have an order")
        return redirect("product", pk=pk)

# reduce product quantity from cart
login_required()
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_query = Order.objects.filter(user=request.user, ordered=False)
    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(user=request.user, item=item, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Item quantity was updated")
            return redirect("order_summary")
        else:
            messages.info(request, "You do not have an order")
            return redirect("order_summary")


# checkingout of ordered products and payment validation
class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {"form":form, "order":order}
        return render(self.request, "store/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                checkout_address = CheckoutAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                order.save()
                messages.info(self.request, "Checkout Was Successful")
                return redirect("home")
            messages.warning(self.request, "Checkout Failed")
            return redirect("checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("order_summary")




