from rest_framework.test import APITestCase
from rest_framework import status
from django.test import override_settings
from GroFul.apps.products.models import Category, Product

# Decouples tests from the Docker network/Redis daemon entirely
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class SearchAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")
        Product.objects.create(title="Apple", price=2.00, category=self.category)
        Product.objects.create(title="Pineapple", price=3.00, category=self.category)
        Product.objects.create(title="Banana", price=1.00, category=self.category)

    def test_autocomplete_prefix_priority(self):
        """Test Rule: Prefix matches should appear before general matches"""
        response = self.client.get('/api/search/suggest/?q=app')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # 'Apple' starts with 'app', 'Pineapple' only contains it
        self.assertEqual(response.data[0]['title'], "Apple")
        self.assertEqual(response.data[1]['title'], "Pineapple")
        
    def test_autocomplete_minimum_characters(self):
        """Test Rule: Minimum 3 characters required"""
        response = self.client.get('/api/search/suggest/?q=ap')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)