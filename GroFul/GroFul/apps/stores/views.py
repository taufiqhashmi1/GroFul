from rest_framework import generics
from django.db.models import Sum
from .models import Inventory
from GroFul.apps.orders.models import Order
from .serializers import InventoryListingSerializer
from GroFul.apps.orders.serializers import OrderListingSerializer

class StoreInventoryListView(generics.ListAPIView):
    serializer_class = InventoryListingSerializer

    def get_queryset(self):
        return Inventory.objects.filter(store_id=self.kwargs['store_id']).select_related(
            'product', 'product__category'
        ).order_by('product__title')

class StoreOrderListView(generics.ListAPIView):
    serializer_class = OrderListingSerializer

    def get_queryset(self):
        return Order.objects.filter(store_id=self.kwargs['store_id']).annotate(
            total_items=Sum('items__quantity_requested')
        ).order_by('-created_at')