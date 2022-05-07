from django.urls import path
from .views import (HomeView, ProductView, add_to_cart, remove_from_cart, index,
                    reduce_quantity_item, Order_summaryView , CheckoutView)
from store import views



urlpatterns = [
    path("register", views.register_request, name="register"),
    
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),

    path("", index, name="index"),
    path("home", HomeView.as_view(), name="home" ),
    path("product/<str:pk>/", ProductView.as_view(), name="product"),
    path("product/add_to_cart/<str:pk>/", add_to_cart, name="add_to_cart"),
    path("product/remove_from_cart/<str:pk>/", remove_from_cart, name="remove_from_cart"),
    path("product/reduce_quantity_item/<str:pk>/", reduce_quantity_item, name="reduce_quantity_item"),
    path("product/order_summary", Order_summaryView.as_view(), name="order_summary"),
    path("product/checkout", CheckoutView.as_view(), name="checkout"),

]