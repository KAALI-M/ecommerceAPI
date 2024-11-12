# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from orders.ordersAPI.serializers import OrderSerializer

# Create Order
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# Read Order List
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# Read Order Detail
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
