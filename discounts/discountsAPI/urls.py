from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiscountViewSet


# Define the router and register the ProductViewSet
router = DefaultRouter()
router.register(r'discounts', DiscountViewSet)

urlpatterns = [
    path('', include(router.urls),),  # Include all routes defined by the router
]