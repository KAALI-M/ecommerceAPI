from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token

class UserViewSetTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@test.com',
            password='regular123'
        )
        
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username='admin_user',
            email='admin@test.com',
            password='admin123'
        )
        
        # Create an API client
        self.client = APIClient()
        
        # URLs
        self.users_list_url = reverse('user-list')
        
    def get_user_detail_url(self, user_id):
        """Helper method to get user detail URL"""
        return reverse('user-detail', args=[user_id])

    def test_create_user_unauthenticated(self):
        """Test that unauthenticated users can create new user accounts"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').exists(), True)
        
    def test_create_user_with_superuser_privileges(self):
        """Test that non-superusers cannot create users with elevated privileges"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'is_superuser': True,
            'is_staff': True
        }
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.is_superuser, False)
        self.assertEqual(new_user.is_staff, False)

    def test_superuser_create_privileged_user(self):
        """Test that superusers can create users with elevated privileges"""
        self.client.force_authenticate(user=self.superuser)
        data = {
            'username': 'newadmin',
            'email': 'newadmin@test.com',
            'password': 'admin123',
            'is_superuser': True,
            'is_staff': True
        }
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(username='newadmin')
        self.assertEqual(new_user.is_superuser, True)
        self.assertEqual(new_user.is_staff, True)

    def test_list_users_authentication(self):
        """Test that only authenticated users can list users"""
        # Unauthenticated request
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Authenticated request
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_permissions(self):
        """Test user retrieval permissions"""
        # Setup another user
        other_user = User.objects.create_user(
            username='other_user',
            email='other@test.com',
            password='other123'
        )
        
        # Unauthenticated request
        response = self.client.get(self.get_user_detail_url(other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Regular user trying to access other user's profile
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.get_user_detail_url(other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Regular user accessing own profile
        response = self.client.get(self.get_user_detail_url(self.regular_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Superuser accessing any profile
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.get_user_detail_url(other_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_permissions(self):
        """Test user update permissions"""
        update_data = {
            'email': 'updated@test.com',
            'is_staff': True,
            'is_superuser': True
        }
        
        # Regular user updating their own profile
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(
            self.get_user_detail_url(self.regular_user.id),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = User.objects.get(id=self.regular_user.id)
        self.assertEqual(updated_user.email, 'updated@test.com')
        self.assertEqual(updated_user.is_staff, False)  # Should not be updated
        self.assertEqual(updated_user.is_superuser, False)  # Should not be updated

    def test_delete_user_permissions(self):
        """Test user deletion permissions"""
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username='delete_me',
            email='delete@test.com',
            password='delete123'
        )
        
        # Regular user trying to delete another user
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.get_user_detail_url(user_to_delete.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Regular user deleting their own profile
        response = self.client.delete(self.get_user_detail_url(self.regular_user.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(id=self.regular_user.id).exists(), False)

    def test_password_write_only(self):
        """Test that password is write-only and not included in responses"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.get_user_detail_url(self.regular_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', response.data)