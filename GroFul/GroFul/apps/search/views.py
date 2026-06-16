from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Value, IntegerField, Case, When, OuterRef, Subquery
from rest_framework.pagination import PageNumberPagination
from GroFul.apps.products.models import Product
from GroFul.apps.stores.models import Inventory
from .serializers import ProductSearchSerializer
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class ProductSearchAPIView(generics.ListAPIView):
    serializer_class = ProductSearchSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        
        # Keyword Search
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) | 
                Q(category__name__icontains=q)
            )
        
        # Metadata Filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
            
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
            
        # Store Inventory Conditional Injection
        store_id = self.request.query_params.get('store_id')
        in_stock = self.request.query_params.get('in_stock')
        
        if store_id:
            inventory_subquery = Inventory.objects.filter(
                product=OuterRef('pk'), 
                store_id=store_id
            ).values('quantity')[:1]
            
            queryset = queryset.annotate(store_quantity=Subquery(inventory_subquery))
            
            if in_stock and in_stock.lower() == 'true':
                queryset = queryset.filter(store_quantity__gt=0)
        
        # Sorting Strategy
        sort_by = self.request.query_params.get('sort', 'newest')
        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == '-price':
            queryset = queryset.order_by('-price')
        elif sort_by == 'relevance' and q:
            # Basic relevance approximation for local DB
            queryset = queryset.annotate(
                is_exact=Case(When(title__iexact=q, then=Value(1)), default=Value(2), output_field=IntegerField())
            ).order_by('is_exact', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset

class ProductSuggestAPIView(generics.ListAPIView):
    # Limits requests to 20 per minute based on the client's IP address. Blocks excess requests.
    @method_decorator(ratelimit(key='ip', rate='20/m', block=True))
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q', '').strip()
        
        if len(q) < 3:
            raise ValidationError({"detail": "Minimum 3 characters required."})
        
        queryset = Product.objects.filter(title__icontains=q).annotate(
            match_order=Case(
                When(title__istartswith=q, then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        ).order_by('match_order', 'title')[:10]
        
        results = [{"id": p.id, "title": p.title} for p in queryset]
        return Response(results)