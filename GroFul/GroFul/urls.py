from django.contrib import admin
from django.urls import path
from GroFul.apps.orders.views import OrderViewSet
from GroFul.apps.stores.views import StoreInventoryListView, StoreOrderListView
from GroFul.apps.search.views import ProductSearchAPIView, ProductSuggestAPIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Orders & Stores
    path('orders/', OrderViewSet.as_view({'post': 'create'}), name='create-order'),
    path('stores/<int:store_id>/inventory/', StoreInventoryListView.as_view(), name='store-inventory'),
    path('stores/<int:store_id>/orders/', StoreOrderListView.as_view(), name='store-orders'),
    
    # Search
    path('api/search/products/', ProductSearchAPIView.as_view(), name='search-products'),
    path('api/search/suggest/', ProductSuggestAPIView.as_view(), name='search-suggest'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]