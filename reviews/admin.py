from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_date')
    search_fields = ('product__name', 'user__username')
    list_filter = ('rating', 'created_date')