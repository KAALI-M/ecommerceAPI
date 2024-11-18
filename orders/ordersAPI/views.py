from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from orders.ordersAPI.serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated

class OrderListView(generics.ListAPIView):
    """
    List orders for the current user.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all orders
        for the currently authenticated user.
        """
        return Order.objects.filter(user=self.request.user)

class OrderCreateView(generics.CreateAPIView):
    """
    Create a new order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an order.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return only orders owned by the current user.
        """
        return Order.objects.filter(user=self.request.user)