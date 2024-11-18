from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from products.models import Product, Category
from .models import Wishlist
from rest_framework import status
from django.urls import reverse

class WishlistAPITestCase(APITestCase):
    def setUp(self):
        """
        Set up the test environment.
        Create test users and products.
        """
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com"
        )
        
        # Create test category
        self.category = Category.objects.create(name="Test Category")
        
        # Create test product - note the lowercase 'category' field name
        self.product = Product.objects.create(
            name="Test Product",
            stock_quantity=100,
            price=9.99,
            category=self.category  # Changed from Category to category
        )
        
        # Force authenticate the user instead of using login
        self.client.force_authenticate(user=self.user)
        
        # Use reverse to generate URLs
        self.wishlist_url = reverse('wishlist-list')  # Make sure this matches your URL name
        
        self.wishlist_data = {
            "name": "My Wishlist",
            "products": [self.product.id]
        }

    def test_create_wishlist_authenticated(self):
        """
        Test that an authenticated user can create a wishlist.
        """
        response = self.client.post(self.wishlist_url, self.wishlist_data, format='json')
        print(f'url: {self.wishlist_url}', f'data: {self.wishlist_data}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.wishlist_data['name'])
        self.assertEqual(response.data['user'], self.user.id)
        # Verify the product was added to the wishlist
        self.assertIn(self.product.id, response.data['products'])

    def test_create_wishlist_unauthenticated(self):
        """
        Test that an unauthenticated user cannot create a wishlist.
        """
        # Clear the authentication
        self.client.force_authenticate(user=None)
        response = self.client.post(self.wishlist_url, self.wishlist_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_wishlist_other_user(self):
        """
        Test that a user cannot create a wishlist for another user.
        """
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpassword",
            email="other@example.com"
        )
        invalid_wishlist_data = {
            "name": "Invalid Wishlist",
            "user": other_user.id,
            "products": [self.product.id]
        }
        print('invalid_wishlist_data', invalid_wishlist_data)
        response = self.client.post(self.wishlist_url, invalid_wishlist_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_wishlist(self):
        """
        Test that an authenticated user can retrieve their own wishlist.
        """
        wishlist = Wishlist.objects.create(user=self.user, name="My Wishlist")
        wishlist.products.add(self.product)
        wishlist_detail_url = reverse('wishlist-detail', kwargs={'pk': wishlist.id})
        response = self.client.get(wishlist_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertIn(self.product.id, response.data['products'])

    def test_get_other_users_wishlist(self):
        """
        Test that a user cannot retrieve another user's wishlist.
        """
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpassword",
            email="other@example.com"
        )
        wishlist = Wishlist.objects.create(user=other_user, name="Other User's Wishlist")
        wishlist.products.add(self.product)
        wishlist_detail_url = reverse('wishlist-detail', kwargs={'pk': wishlist.id})
        print('wishlist_detail_url', wishlist_detail_url)
        response = self.client.get(wishlist_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist(self):
        """
        Test that a user can update their own wishlist.
        """
        wishlist = Wishlist.objects.create(user=self.user, name="Original Name")
        wishlist.products.add(self.product)
        wishlist_detail_url = reverse('wishlist-detail', kwargs={'pk': wishlist.id})
        update_data = {
            "name": "Updated Name",
            "products": [self.product.id]
        }
        response = self.client.put(wishlist_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Name")

    def test_delete_wishlist(self):
        """
        Test that a user can delete their own wishlist.
        """
        wishlist = Wishlist.objects.create(user=self.user, name="To Be Deleted")
        wishlist.products.add(self.product)
        wishlist_detail_url = reverse('wishlist-detail', kwargs={'pk': wishlist.id})
        response = self.client.delete(wishlist_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Wishlist.objects.filter(id=wishlist.id).exists())