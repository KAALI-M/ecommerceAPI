from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet

# Define the router and register the ProductViewSet
router = DefaultRouter()
router.register(r'ProductCategory', ProductCategoryViewSet)

urlpatterns = [
    path('', include(router.urls) ),  # Include all routes defined by the router
]