from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet

# Create a router and register our WishlistViewSet with it.
router = DefaultRouter()
router.register(r'wishlists', WishlistViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the viewset routes under the 'api/' prefix
]
