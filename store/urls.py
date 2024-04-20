from django.urls import path
from . import views


urlpatterns = [
    path('', views.product_list_api_views,name='home'),
    path('products/<int:id>/', views.product_details_api_view, name='products')
]