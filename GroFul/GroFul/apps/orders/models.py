#orders/models.py

from django.db import models
from GroFul.apps.stores.models import Store
from GroFul.apps.products.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        REJECTED = 'REJECTED', 'Rejected'

    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.PENDING,
        db_index=True # Indexed for fast O(1) status filtering
    )
    # Indexed because the assignment requires sorting by newest first
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.store.name} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_requested = models.PositiveIntegerField()

    class Meta:
        # Prevents the same product from being added to an order twice on different rows
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'], 
                name='unique_order_product_item'
            )
        ]

    def __str__(self):
        return f"{self.quantity_requested}x {self.product.title}"