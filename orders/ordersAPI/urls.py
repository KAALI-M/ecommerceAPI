from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.ordersAPI.views import OrderViewSet

# Define the router and register the OrderViewSet
router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls))
]
