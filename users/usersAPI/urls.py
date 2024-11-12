from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet

# Define the router and register the ProductViewSet
router = DefaultRouter()
router.register(r'users', UsersViewSet)

urlpatterns = [
    path('', include(router.urls) ),  # Include all routers
]