#stores/models.py

from django.db import models
from GroFul.apps.products.models import Product

class Store(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    location = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_inventories')
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Inventories"
        # Enforces exactly one inventory row per product per store at the database level
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'product'], 
                name='unique_store_product_inventory'
            )
        ]

    def __str__(self):
        return f"{self.store.name} - {self.product.title}: {self.quantity}"