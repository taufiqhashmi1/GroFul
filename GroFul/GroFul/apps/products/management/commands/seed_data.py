import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
# Since your apps are inside GroFul/apps, import them using GroFul.apps...
from GroFul.apps.products.models import Category, Product
from GroFul.apps.stores.models import Store, Inventory

class Command(BaseCommand):
    help = 'Seeds the database with foundational categories, products, stores, and inventories'

    def handle(self, *args, **options):
        fake = Faker()
        self.stdout.write("Starting data seeding processes...")

        with transaction.atomic():
            # 1. Categories
            self.stdout.write("Generating categories...")
            category_names = [
                "Fresh Vegetables", "Dairy & Eggs", "Bakery", "Beverages", 
                "Snacks & Munchies", "Meat & Seafood", "Frozen Foods", 
                "Pantry Staples", "Personal Care", "Household Items"
            ]
            categories = [Category(name=name) for name in category_names]
            Category.objects.bulk_create(categories, ignore_conflicts=True)
            all_categories = list(Category.objects.all())

            # 2. Products
            self.stdout.write("Generating 1000 products...")
            products_to_create = []
            for _ in range(1050):
                products_to_create.append(
                    Product(
                        title=f"{fake.word().capitalize()} {fake.word().capitalize()} {random.randint(10,99)}g",
                        description=fake.paragraph(nb_sentences=2),
                        price=round(random.uniform(10.0, 500.0), 2),
                        category=random.choice(all_categories)
                    )
                )
            Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
            all_products = list(Product.objects.all())

            # 3. Stores
            self.stdout.write("Generating 22 stores...")
            stores_to_create = []
            for _ in range(22):
                stores_to_create.append(
                    Store(
                        name=f"Aforro Hub - {fake.city()}",
                        location=fake.address().replace('\n', ', ')
                    )
                )
            Store.objects.bulk_create(stores_to_create, ignore_conflicts=True)
            all_stores = list(Store.objects.all())

            # 4. Inventory Junctions
            self.stdout.write("Assigning inventory records per store...")
            inventory_records = []
            
            for store in all_stores:
                selected_products = random.sample(all_products, k=350)
                for product in selected_products:
                    inventory_records.append(
                        Inventory(
                            store=store,
                            product=product,
                            quantity=random.randint(0, 100)
                        )
                    )
            
            Inventory.objects.bulk_create(inventory_records, batch_size=2000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Successfully seeded all backend datasets!"))