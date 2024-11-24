from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from categories.models import Category
from django.contrib.contenttypes.models import ContentType

class ProductCategoryViewSetTests(TestCase):
    def setUp(self):
        """Set up test data and users with different permission levels"""
        self.client = APIClient()
        
        # Create test users
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@test.com',
            password='superpass123'
        )
        
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@test.com',
            password='normalpass123'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@test.com',
            password='staffpass123'
        )
        
        # Get content type for product model
        self.content_type = ContentType.objects.get(app_label='categories', model='category')
        
        # Add permissions to staff user
        self.add_permission = Permission.objects.get(
            content_type=self.content_type,
            codename='add_category'
        )
        self.change_permission = Permission.objects.get(
            content_type=self.content_type,
            codename='change_category'
        )
        self.delete_permission = Permission.objects.get(
            content_type=self.content_type,
            codename='delete_category'
        )
        
        self.staff_user.user_permissions.add(
            self.add_permission,
            self.change_permission,
            self.delete_permission
        )
        
        # Create test category
        self.category = Category.objects.create(name='Test Category')
        
        # Define common URLs
        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', kwargs={'pk': self.category.pk})

    def test_list_categories_unauthenticated(self):
        """Test that unauthenticated users can list categories"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')

    def test_create_category_unauthenticated(self):
        """Test that unauthenticated users cannot create categories"""
        data = {'name': 'New Category'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_authenticated_no_permission(self):
        """Test that authenticated users without permissions cannot create categories"""
        self.client.force_authenticate(user=self.normal_user)
        data = {'name': 'New Category'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_with_permission(self):
        """Test that users with proper permissions can create categories"""
        self.client.force_authenticate(user=self.staff_user)
        data = {'name': 'New Category'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)


    def test_create_category_superuser(self):
        """Test that superuser can create categories"""
        self.client.force_authenticate(user=self.superuser)
        data = {'name': 'Super Category'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_update_category_with_permission(self):
        """Test that users with proper permissions can update categories"""
        self.client.force_authenticate(user=self.staff_user)
        data = {'name': 'Updated Category'}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_partial_update_category_with_permission(self):
        """Test that users with proper permissions can partially update categories"""
        self.client.force_authenticate(user=self.staff_user)
        data = {'name': 'Partially Updated Category'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Partially Updated Category')

    def test_delete_category_with_permission(self):
        """Test that users with proper permissions can delete categories"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_delete_category_without_permission(self):
        """Test that users without proper permissions cannot delete categories"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), 1)

    def test_superuser_full_access(self):
        """Test that superuser has full access to all operations"""
        self.client.force_authenticate(user=self.superuser)
        
        # Test create
        create_response = self.client.post(self.list_url, {'name': 'Super Category'})
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        # Test update
        update_response = self.client.put(self.detail_url, {'name': 'Updated Super Category'})
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # Test delete
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)