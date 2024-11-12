from django.db import models
from django.contrib.auth.models import User
from products.models import Product


# Create your models here.
class Wishlist(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    products = models.ManyToManyField(Product, related_name="wishlists")
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"