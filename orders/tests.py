from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from orders.models import Order
from products.models import Product
from categories.models import Category

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta


class OrderViewSetTest(TestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')
        self.superuser_token = self.get_token(self.superuser)

        # Create a staff user
        self.staff_user = User.objects.create_user(username='staff', password='staff123', email='staff@example.com', is_staff=True)
        self.staff_user_token = self.get_token(self.staff_user)

        # Create a regular user
        self.user = User.objects.create_user(username='user', password='user123', email='user@example.com')
        self.user_token = self.get_token(self.user)

        # Create another regular user
        self.other_user = User.objects.create_user(username='other_user', password='other123', email='other@example.com')
        self.other_user_token = self.get_token(self.other_user)

        # Create a category
        self.category = Category.objects.create(name="Sample Category")  # Adjust fields as needed

        # Create a product with the category
        self.product = Product.objects.create(
            name="Sample Product",
            price=100.00,
            stock_quantity=200,
            category=self.category,  # Pass the created category here
        )

        # Create sample orders
        self.order1 = Order.objects.create(user=self.user, product=self.product, quantity=10)
        self.order2 = Order.objects.create(user=self.other_user, product=self.product, quantity=15)

        # API client for requests
        self.client = APIClient()

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_orders_authenticated_user(self):
        """Test that authenticated users can only access their own orders"""
        self.authenticate(self.user_token)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # User has only 1 order
        self.assertEqual(response.data[0]['id'], self.order1.id)

    def test_get_orders_superuser(self):
        """Test that superusers can access all orders"""
        self.authenticate(self.superuser_token)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Superuser can access all orders

    def test_post_order_authenticated_user(self):
        """Test that authenticated users can create orders"""
        self.authenticate(self.user_token)
        data = {
            "total": 200.00,
            "created_at": datetime.now(),
        }
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 3)  # A new order is created
        self.assertEqual(Order.objects.last().user, self.user)  # Ensure the order is associated with the current user

    def test_post_order_unauthenticated(self):
        """Test that unauthenticated users cannot create orders"""
        data = {
            "total": 200.00,
            "created_at": datetime.now(),
        }
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_order_owner(self):
        """Test that users can update their own orders"""
        self.authenticate(self.user_token)
        data = {
            "total": 120.00,
        }
        response = self.client.put(f'/api/orders/{self.order1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.total, 120.00)

    def test_put_order_not_owner(self):
        """Test that users cannot update orders they do not own"""
        self.authenticate(self.user_token)
        data = {
            "total": 120.00,
        }
        response = self.client.put(f'/api/orders/{self.order2.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_owner(self):
        """Test that users can delete their own orders"""
        self.authenticate(self.user_token)
        response = self.client.delete(f'/api/orders/{self.order1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.filter(id=self.order1.id).count(), 0)

    def test_delete_order_not_owner(self):
        """Test that users cannot delete orders they do not own"""
        self.authenticate(self.user_token)
        response = self.client.delete(f'/api/orders/{self.order2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_orders_staff_user(self):
        """Test that staff users can access all orders"""
        self.authenticate(self.staff_user_token)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print ("response : ",response)
        self.assertEqual(len(response.data), 2)  # Staff can access all orders

    def test_get_orders_unauthenticated(self):
        """Test that unauthenticated users cannot view orders"""
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
