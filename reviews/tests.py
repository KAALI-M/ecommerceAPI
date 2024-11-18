from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from products.models import Product, Category  # Import Category
from .models import Review

class ReviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a category first
        self.category = Category.objects.create(name='Test Category')
        
        # Then create a product with the category
        self.product = Product.objects.create(
            name='Test Product', 
            description='Test Description', 
            stock_quantity=10, 
            price=10.00,
            category=self.category  # Add the category
        )

    def test_create_review(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'product': self.product.id,
            'rating': 4,
            'comment': 'Great product!'
        }
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().user, self.user)

    def test_invalid_rating(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'product': self.product.id,
            'rating': 6,
            'comment': 'Invalid rating'
        }
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, 400)

    def test_unauthorized_review_creation(self):
        data = {
            'product': self.product.id,
            'rating': 4,
            'comment': 'Unauthorized review'
        }
        response = self.client.post('/api/reviews/', data)
        self.assertEqual(response.status_code, 401)