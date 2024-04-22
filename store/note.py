from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from store.models import Product, Collection
from store.api.serializers import ProductSerializer, CollectionSerializers
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Count


class ProductListApiView(ListCreateAPIView):
    get_queryset = Product.objects.select_related('collection').all()
    get_serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}

class ProductDetailsApiView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({"error": "Product cannot be deleted because it associated with an order items ."})
        product.delete()
# ================================ note =============================
# by using viewsets we can combine to or more view 
class ProductViewSet(ModelViewSet):
    get_queryset = Product.objects.all()
    get_serializer_class = ProductSerializer
    
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({"error": "Product cannot be deleted because it associated with an order items ."})
        product.delete()

class CollectionViewSet(ModelViewSet):
    queryset = collection = Collection.objects.annotate(
            product_count=Count('products'))
    serializer_class = CollectionSerializers
    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.annotate(
            product_count=Count('products')), pk=pk)
        if collection.products.count() > 0:
            return Response({"error": "Collection cannot be deleted because it includes one or more  products."})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)