from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    


    def __str__(self):
        return self.name
    

class Image(models.Model):
    image = models.ImageField(upload_to='product_images/', blank=True)  # Use ImageField for image uploads
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    class meta:
        permissons = [
            ("manage_images","Can manage images")
            
        ]
    def __str__(self):
        return f"Image for {self.product.name}"
