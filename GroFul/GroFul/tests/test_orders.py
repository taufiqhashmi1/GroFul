from rest_framework.test import APITestCase
from rest_framework import status
from GroFul.apps.products.models import Category, Product
from GroFul.apps.stores.models import Store, Inventory
from GroFul.apps.orders.models import Order

class OrderAPITests(APITestCase):
    def setUp(self):
        # Generate test data isolated from the main database
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            title="Test Product", price=10.00, category=self.category
        )
        self.store = Store.objects.create(name="Test Store", location="Test Location")
        self.inventory = Inventory.objects.create(
            store=self.store, product=self.product, quantity=5
        )
        self.url = '/orders/'

    def test_create_order_sufficient_stock(self):
        """Test Rule 3: Sufficient stock deducts quantity and confirms order"""
        data = {
            "store_id": self.store.id,
            "items": [{"product_id": self.product.id, "quantity_requested": 2}]
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "CONFIRMED")
        
        # Verify database mutation
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 3)

    def test_create_order_insufficient_stock(self):
        """Test Rule 2: Insufficient stock rejects order and prevents deduction"""
        data = {
            "store_id": self.store.id,
            "items": [{"product_id": self.product.id, "quantity_requested": 10}]
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], "REJECTED")
        
        # Verify transaction rollback preserved the inventory
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)