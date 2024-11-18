from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from discounts.models import Discount
from products.models import Product

class DiscountViewSetTests(APITestCase):
    def setUp(self):
        # Create test users with different permission levels
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='adminpass'
        )
        self.regular_user = User.objects.create_user(
            username='regular', 
            password='regularpass'
        )
        
        # Assign permissions to admin user
        permissions = Permission.objects.filter(
            codename__in=['add_product', 'change_product', 'delete_product']
        )
        self.admin_user.user_permissions.set(permissions)

        
        # Create test data
        self.discount1 = Discount.objects.create(
            name='Test Discount 1',
            amount=10.00,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.discount2 = Discount.objects.create(
            name='Test Discount 2',
            amount=20.00,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=40)
        )
        
        # API client setup
        self.client = APIClient()
        self.url = reverse('discount-list')

    def test_list_discounts_unauthenticated(self):
        """Test that unauthenticated users can list discounts"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Assuming pagination is enabled

    def test_create_discount_unauthenticated(self):
        """Test that unauthenticated users cannot create discounts"""
        new_discount = {
            'name': 'New Discount',
            'amount': 15.00,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=20)
        }
        response = self.client.post(self.url, new_discount)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_discount_authenticated_with_permission(self):
        """Test that authenticated users with proper permissions can create discounts"""
        self.client.force_authenticate(user=self.admin_user)
        new_discount = {
            'name': 'New Discount',
            'amount': 15.00,
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=20)).isoformat()
        }
        response = self.client.post(self.url, new_discount)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discount.objects.count(), 3)

    def test_update_discount_authenticated_with_permission(self):
        """Test that authenticated users with proper permissions can update discounts"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('discount-detail', kwargs={'pk': self.discount1.pk})
        updated_data = {
            'name': 'Updated Discount',
            'amount': 25.00,
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        }
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.discount1.refresh_from_db()
        self.assertEqual(self.discount1.name, 'Updated Discount')

    def test_delete_discount_authenticated_with_permission(self):
        """Test that authenticated users with proper permissions can delete discounts"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('discount-detail', kwargs={'pk': self.discount1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Discount.objects.count(), 1)

    def test_filter_by_included_date(self):
        """Test filtering discounts by included date"""
        test_date = date.today() + timedelta(days=35)
        response = self.client.get(f"{self.url}?included_date={test_date.isoformat()}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only discount2 should be included as it covers the test date
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Discount 2')

    def test_pagination(self):
        """Test pagination functionality"""
        # Create additional discounts to test pagination
        for i in range(15):
            Discount.objects.create(
                name=f'Pagination Test Discount {i}',
                amount=10.00,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30)
            )
        
        # Test default pagination (10 items per page)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Test custom page size
        response = self.client.get(f"{self.url}?page_size=5")
        self.assertEqual(len(response.data['results']), 5)
        
        # Test second page
        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(len(response.data['results']), 7)  # 17 total items, page 2 should have 7 items

    def test_max_page_size_limit(self):
        """Test that page size cannot exceed max_page_size"""
        response = self.client.get(f"{self.url}?page_size=200")  # Max is 100
        self.assertEqual(len(response.data['results']), min(Discount.objects.count(), 100))