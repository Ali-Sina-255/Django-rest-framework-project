from django.urls import path
from . import views
# from rest_framework.routers import DefaultRouter 
# from pprint import pprint
from rest_framework_nested import routers  # type: ignore

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collection', views.CollectionViewSet)
router.register('review', views.ReviewViewSet)
router.register('carts', views.CartViewSet)
router.register('customer', views.CustomerViewSet)
product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

carts_routers = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_routers.register('items', views.CartItemViewSet, basename='cart-items')
# tow way to use Router
# 1. urlpatterns =router.urls
# 2. use include(path('',include(router.url)))

urlpatterns = router.urls + product_router.urls + carts_routers.urls

# urlpatterns = [
#     # path('products', views.ProductListApiView.as_view(),name='home'),
#     # path('products/<int:pk>/', views.ProductDetailsApiView.as_view(), name='products'),
#     # path('collection/', views.CollectionListApiView.as_view(), name='collection'),
#     # path('collection/<int:pk>/', views.CollectionDetailsAPIView.as_view(), name='collection-detail'),
# ]
