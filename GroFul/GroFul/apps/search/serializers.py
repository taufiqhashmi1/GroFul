from rest_framework import serializers
from GroFul.apps.products.models import Product

class ProductSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    # This field is populated dynamically via database annotation if store_id is provided
    store_quantity = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category_name', 'store_quantity', 'created_at']