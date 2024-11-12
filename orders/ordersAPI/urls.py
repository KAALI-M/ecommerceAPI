
from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),  # List all orders
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),  # Create a new order
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),  # Retrieve, update or delete an order
]
