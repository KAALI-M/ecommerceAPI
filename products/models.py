from django.db import models
from django.core.validators import MinValueValidator
from categories.models import Category


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.name

class Image(models.Model):
    image = models.ImageField(upload_to='product_images/', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    class Meta:
        permissions = [
            ("manage_images", "Can manage images")
        ]

    def __str__(self):
        return f"Image for {self.product.name}"