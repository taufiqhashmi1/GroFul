#apps/orders/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from GroFul.apps.stores.models import Inventory
from .serializers import OrderCreateSerializer
from .tasks import send_order_confirmation

class OrderViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        store_id = serializer.validated_data['store_id']
        items_data = serializer.validated_data['items']
        
        with transaction.atomic():
            order = Order.objects.create(store_id=store_id, status=Order.Status.PENDING)
            insufficient_stock = False
            order_items_to_create = []
            
            product_ids = [item['product_id'] for item in items_data]
            inventories = Inventory.objects.select_for_update().filter(
                store_id=store_id, product_id__in=product_ids
            )
            inventory_map = {inv.product_id: inv for inv in inventories}
            
            for item in items_data:
                p_id = item['product_id']
                req_qty = item['quantity_requested']
                inv = inventory_map.get(p_id)
                
                if not inv or inv.quantity < req_qty:
                    insufficient_stock = True
                    break 
                
                inv.quantity -= req_qty
                # Assign order_id explicitly to prevent model state caching anomalies during bulk_create
                order_items_to_create.append(OrderItem(order_id=order.id, product_id=p_id, quantity_requested=req_qty))
            
            if insufficient_stock:
                order.status = Order.Status.REJECTED
                order.save()
                return Response(
                    {"status": "REJECTED", "order_id": order.id, "message": "Insufficient stock."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save deductions to inventory
            Inventory.objects.bulk_update(inventories, ['quantity'])
            
            # Safe sequential save loop to prevent SQLite primary key collision bugs
            for order_item in order_items_to_create:
                order_item.save()
                
            order.status = Order.Status.CONFIRMED
            order.save()
            
            # Trigger background async task
            send_order_confirmation.delay(order.id)
            
            return Response({"status": "CONFIRMED", "order_id": order.id}, status=status.HTTP_201_CREATED)