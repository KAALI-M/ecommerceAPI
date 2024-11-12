from products.models import Product
from django.db import models

# Create your models here.
class Discount(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField() 
    products = models.ManyToManyField(Product, through='ProductDiscount', related_name="discounts")

    def __str__(self):
        return f"Discount of {self.amount} valid from {self.start_date} to {self.end_date}"

class ProductDiscount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

