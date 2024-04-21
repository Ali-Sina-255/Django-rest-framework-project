from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProductListApiView.as_view(),name='home'),
    path('products/<int:id>/', views.ProductDetailsApiView.as_view(), name='products'),
    path('collection/', views.CollectionListApiView.as_view(), name='collection'),
    path('collection/<int:id>/', views.collection_detail_api_views, name='collection-detail'),
]