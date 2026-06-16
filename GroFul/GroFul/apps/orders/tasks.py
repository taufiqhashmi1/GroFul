import time
from celery import shared_task
from .models import Order

@shared_task
def send_order_confirmation(order_id):
    """
    Simulates a time-consuming background task like generating a PDF receipt 
    or sending an email via an external SMTP provider.
    """
    try:
        order = Order.objects.get(id=order_id)
        # Simulate a 3-second network delay
        time.sleep(3)
        print(f"SUCCESS: Order Confirmation Email sent to store '{order.store.name}' for Order #{order.id}.")
        return True
    except Order.DoesNotExist:
        return False