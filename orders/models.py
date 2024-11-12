from django.db import models
from products.models import Product
from django.conf import settings
from django.core.exceptions import ValidationError

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Check if there is enough stock before saving the order
        if self.product.stock_quantity < self.quantity:
            raise ValidationError("Not enough stock available for this product.")

        # Reduce the stock quantity
        self.product.stock_quantity -= self.quantity
        self.product.save()  # Save the product with updated stock

        # Save the order
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.user} for {self.product.name}"

