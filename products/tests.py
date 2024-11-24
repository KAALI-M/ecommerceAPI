from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User, Permission
from .models import Product, Category
from decimal import Decimal


class ProductAPITestCase(TestCase):

    def setUp(self):
        # Create a category instance for the product
        self.category = Category.objects.create(name="Electronics")

        # Create a user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        # Create a product with the created category
        self.product = Product.objects.create(
            name="Smartphone",
            description="Latest model smartphone",
            price=Decimal("598.99"),
            stock_quantity=49,
            category=self.category  # Assign the created category
        )

        # Initialize API client
        self.client = APIClient()

        # Define URL for product list and detail
        self.list_url = reverse('product-list')
        self.detail_url = reverse('product-detail', args=[self.product.id])

        # Obtain JWT token for authentication
        self.token_url = reverse('token_obtain_pair')
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpass'
        })

        # Ensure token retrieval was successful
        if response.status_code == status.HTTP_200_OK:
            self.token = response.data['access']
        else:
            self.fail("Token authentication setup failed in setUp.")

    def authenticate(self, permissions=None):
        """Helper method to authenticate the client and add permissions."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        if permissions:
            for perm in permissions:
                permission = Permission.objects.get(codename=perm)
                self.user.user_permissions.add(permission)

    # Test creating a product without permissions (should fail)
    def test_create_product_no_permissions(self):
        """Test creating a product without permissions (should fail)"""
        self.authenticate()
        data = {
            "name": "New Product",
            "description": "Description",
            "price": Decimal("298.99"),
            "stock_quantity": 19,
            "category": self.category.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test creating a product with correct permissions
    def test_create_product_with_permissions(self):
        """Test creating a product with the required permissions."""
        self.authenticate(permissions=['add_product'])
        data = {
            "name": "New Product",
            "description": "Description",
            "price": Decimal("298.99"),
            "stock_quantity": 19,
            "category": self.category.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)  # One more product added

    # Test retrieving product list
    def test_get_product_list(self):
        """Test retrieving the product list with required permissions."""
        self.authenticate(permissions=['view_product'])
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # One product in setUp

    # Test retrieving product detail
    def test_get_product_detail(self):
        """Test retrieving a single product by ID with permissions."""
        self.authenticate(permissions=['view_product'])
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    # Test updating product details
    def test_update_product(self):
        """Test updating a product's details with required permissions."""
        self.authenticate(permissions=['change_product'])
        data = {
            "name": "Updated Product",
            "description": "Updated description",
            "price": Decimal("19.99"),
            "stock_quantity": 74,
            "category": self.category.id
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(self.product.price, Decimal("19.99"))

    # Test deleting a product
    def test_delete_product(self):
        """Test deleting a product with required permissions."""
        self.authenticate(permissions=['delete_product'])
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)