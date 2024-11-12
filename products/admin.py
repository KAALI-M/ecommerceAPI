from django.contrib import admin
from .models import Product, Category, Image

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'created_date', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'created_date')
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')