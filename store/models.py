from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField
from django.urls import reverse



CATEGORY = (
    ('Shirt', 'Shirt'),
    ('SportWear', 'Sport Wear'),
    ('OutWear', 'Out Wear')
)

LABEL = (
    ('New', 'New'),
    ('BestSeller', 'Best Seller')
)

class Item(models.Model) :
    item_name = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY, max_length=20)
    label = models.CharField(choices=LABEL, max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse("product", kwargs={"pk": self.pk})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={"pk": self.pk})

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={"pk": self.pk})


class OrderItem(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.item_name}"

    def get_total_item_prize(self):
        return self.quantity * self.item.price

    def get_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_save(self):
        return self.get_total_item_prize() - self.get_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_discount_item_price()
        return self.get_total_item_prize()


class Order(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class CheckoutAddress(models.Model):
    PAYMENT = (
        ("Stripe", "Stripe"),
        ("PayPal", "PayPal"),
        ("MasterCard", "MasterCard"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    apartment_address = models.CharField(max_length=200)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=200)
    # same_billing_address = models.BooleanField(default=False)
    # save_info = models.BooleanField(default=False)
    # payment_option = models.CharField( max_length=200, choices=PAYMENT )

    def __str__(self):
        return f"self.user.username from self.country"
