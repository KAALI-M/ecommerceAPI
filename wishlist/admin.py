from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_date')
    filter_horizontal = ('products',)  # Allows selection of multiple products in the wishlist