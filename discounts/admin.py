from django.contrib import admin
from .models import Discount, ProductDiscount, Product

class ProductDiscountInline(admin.TabularInline):
    model = ProductDiscount
    extra = 1  # Number of extra blank inlines to display

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('amount', 'start_date', 'end_date')
    inlines = [ProductDiscountInline]  # Add the inline to manage related products