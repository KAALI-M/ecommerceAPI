from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from wishlist.models import Wishlist
from products.models import Product
from categories.models import Category
from rest_framework_simplejwt.tokens import RefreshToken

class WishlistViewSetTest(APITestCase):
    def setUp(self):


        # Create users
        self.superuser = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')
        self.staff_user = User.objects.create_user(username='staff', password='staff123', email='staff@example.com', is_staff=True)
        self.user = User.objects.create_user(username='user', password='user123', email='user@example.com')
        self.other_user = User.objects.create_user(username='other_user', password='other123', email='other@example.com')

        # Generate JWT tokens
        self.superuser_token = self.get_token(self.superuser)
        self.staff_user_token = self.get_token(self.staff_user)
        self.user_token = self.get_token(self.user)
        self.other_user_token = self.get_token(self.other_user)

        
        # Create a category first
        self.category = Category.objects.create(name='Test Category')
        # Create sample products
        self.product1 = Product.objects.create(name="Product 1", price=50.00, stock_quantity=100,category=self.category  )
        self.product2 = Product.objects.create(name="Product 2", price=30.00, stock_quantity=200, category=self.category )

        # Create sample wishlists
        self.wishlist1 = Wishlist.objects.create(name="User Wishlist", user=self.user)
        self.wishlist1.products.set([self.product1, self.product2])

        self.wishlist2 = Wishlist.objects.create(name="Other User Wishlist", user=self.other_user)
        self.wishlist2.products.set([self.product1])

        # API client
        self.client = APIClient()

    def get_token(self, user):
        """Generate JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, token):
        """Authenticate the client with the provided token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_wishlists_authenticated_user(self):
        """Test that authenticated users can only access their own wishlists."""
        self.authenticate(self.user_token)
        response = self.client.get('/api/wishlists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.wishlist1.id)

    def test_get_wishlists_superuser(self):
        """Test that superusers can access all wishlists."""
        self.authenticate(self.superuser_token)
        response = self.client.get('/api/wishlists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_wishlist_authenticated_user(self):
        """Test that authenticated users can create wishlists."""
        self.authenticate(self.user_token)
        data = {
            "name": "New Wishlist",
            "products": [self.product1.id]
        }
        response = self.client.post('/api/wishlists/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wishlist.objects.count(), 3)
        self.assertEqual(Wishlist.objects.last().user, self.user)

    def test_create_wishlist_unauthenticated(self):
        """Test that unauthenticated users cannot create wishlists."""
        data = {
            "name": "Unauthorized Wishlist",
            "products": [self.product1.id]
        }
        response = self.client.post('/api/wishlists/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_wishlist_owner(self):
        """Test that users can update their own wishlists."""
        self.authenticate(self.user_token)
        data = {
            "name": "Updated Wishlist",
            "products": [self.product2.id]
        }
        response = self.client.put(f'/api/wishlists/{self.wishlist1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wishlist1.refresh_from_db()
        self.assertEqual(self.wishlist1.name, "Updated Wishlist")

    def test_update_wishlist_not_owner(self):
        """Test that users cannot update wishlists they do not own."""
        self.authenticate(self.user_token)
        data = {
            "name": "Hacked Wishlist",
            "products": [self.product2.id]
        }
        response = self.client.put(f'/api/wishlists/{self.wishlist2.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wishlist_owner(self):
        """Test that users can delete their own wishlists."""
        self.authenticate(self.user_token)
        response = self.client.delete(f'/api/wishlists/{self.wishlist1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Wishlist.objects.filter(id=self.wishlist1.id).count(), 0)

    def test_delete_wishlist_not_owner(self):
        """Test that users cannot delete wishlists they do not own."""
        self.authenticate(self.user_token)
        response = self.client.delete(f'/api/wishlists/{self.wishlist2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_wishlists_staff_user(self):
        """Test that staff users can access all wishlists."""
        self.authenticate(self.staff_user_token)
        response = self.client.get('/api/wishlists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_wishlists_unauthenticated(self):
        """Test that unauthenticated users cannot view wishlists."""
        response = self.client.get('/api/wishlists/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

