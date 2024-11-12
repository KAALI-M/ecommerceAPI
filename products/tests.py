from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User, Permission
from .models import Product,Category,Image
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
            price=599.99,
            stock_quantity=50,
            category=self.category  # Assign the created category 
        )

        self.client = APIClient()
        # Define URL for the product list and detail
        self.list_url = reverse('product-list')  
        self.detail_url = reverse('product-detail', args=[self.product.id]) 

        # Get JWT token for authentication
        self.Token_URL = reverse('token_obtain_pair')
        response = self.client.post(self.Token_URL, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.token = response.data['access']

    #test without permissions
    def test_create_product(self):
        """Test creating a product without permissions (should fail)"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        data = {
            "name": "New Product",
            "description": "Description",
            "price": 299.99,
            "stock_quantity": 20,
            "category": self.category.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Expect forbidden if no permission
    
    def test_get_product_list(self):
        """Test retrieving the list of products"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    #test with permissions
    def test_create_product(self):
        # Test logic to verify the product creation
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        permission= Permission.objects.get(codename="add_product")
        self.user.user_permissions.add(permission)
        data = {
            "name": "New Product",
            "description": "Description",
            "price": 299.99,
            "stock_quantity": 20,
            "category": self.category.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_product_list(self):
        """Test retrieving the list of products"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        permission= Permission.objects.get(codename="view_product")
        self.user.user_permissions.add(permission)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one product created in setUp
    
    def test_update_product(self):
        """Test updating a product's details"""

        data = {
            "name": "Updated Product",
            "description": "Updated description",
            "price": 20.99,
            "stock_quantity": 75,
            "category": self.category.id
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        permission= Permission.objects.get(codename="change_product")
        self.user.user_permissions.add(permission)
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(self.product.price, Decimal("20.99"))
    
    
    def test_get_product_detail(self):
        """Test retrieving a single product by ID"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        permission= Permission.objects.get(codename="view_product")
        self.user.user_permissions.add(permission)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    

    def test_delete_product(self):
        """Test deleting a product"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        permission= Permission.objects.get(codename="delete_product")
        self.user.user_permissions.add(permission)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

