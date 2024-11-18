from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from orders.models import Order
from products.models import Product, Category
from orders.ordersAPI.serializers import OrderSerializer

class OrderViewSetTests(APITestCase):
    """Test cases for Order ViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create second user for permission tests
        self.another_user = self.User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpass123'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Test Category'
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            stock_quantity=10,
            category=self.category
        )
        
        # Create order data
        self.valid_order_data = {
            'user': self.user.id,
            'product': self.product.id,
            'quantity': 2
        }
        
        # Create sample order for the main test user
        self.order = Order.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
        
        # Define common URLs
        self.list_url = reverse('order-list')
        self.detail_url = reverse('order-detail', kwargs={'pk': self.order.pk})
        self.create_url = reverse('order-create')

    def test_list_orders_user_specific(self):
        """Test that users can only see their own orders"""
        # Create an order for another user
        other_order = Order.objects.create(
            user=self.another_user,
            product=self.product,
            quantity=1
        )
        
        # Test with main user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see their own order
        self.assertEqual(response.data[0]['user'], self.user.id)
        
        # Test with other user
        self.client.force_authenticate(user=self.another_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see their own order
        self.assertEqual(response.data[0]['user'], self.another_user.id)


    def test_list_orders_authenticated(self):
        """Test that authenticated users can list orders"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_orders_unauthenticated(self):
        """Test that unauthenticated users cannot list orders"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_success(self):
        """Test successful order creation"""
        response = self.client.post(self.create_url, self.valid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(response.data['quantity'], 2)

    def test_create_order_invalid_data(self):
        """Test order creation with invalid data"""
        invalid_data = self.valid_order_data.copy()
        invalid_data['quantity'] = -1
        response = self.client.post(self.create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_insufficient_stock(self):
        """Test order creation with insufficient stock"""
        invalid_data = self.valid_order_data.copy()
        invalid_data['quantity'] = 11  # More than available stock
        response = self.client.post(self.create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order(self):
        """Test retrieving a specific order"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 1)

    def test_retrieve_nonexistent_order(self):
        """Test retrieving a nonexistent order"""
        url = reverse('order-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order(self):
        """Test updating an order"""
        update_data = {
            'user': self.user.id,
            'product': self.product.id,
            'quantity': 3
        }
        response = self.client.put(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 3)



    def test_delete_order(self):
        """Test deleting an order"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_nonexistent_order(self):
        """Test deleting a nonexistent order"""
        url = reverse('order-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_orders_filter_by_user(self):
        """Test filtering orders by user"""
        # Create order for another user
        Order.objects.create(
            user=self.another_user,
            product=self.product,
            quantity=1
        )
        
        # Verify current user only sees their orders
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.id)

    def test_update_order_insufficient_stock(self):
        """Test updating order with insufficient stock"""
        update_data = {
            'user': self.user.id,
            'product': self.product.id,
            'quantity': 11  # More than available stock
        }
        response = self.client.put(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_fields(self):
        """Test order creation with missing required fields"""
        invalid_data = {}
        response = self.client.post(self.create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)
        self.assertIn('product', response.data)
        self.assertIn('quantity', response.data)