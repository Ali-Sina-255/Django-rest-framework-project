from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
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


# =============================function base views ========================
@api_view(["GET", "POST"])
def product_list_api_views(request):
    if request.method == 'GET':
        product = Product.objects.all()
        print(product)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET', 'PUT', "DELETE"])
def product_details_api_view(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response(
            {"error": {
                "code": 404,
                "message": f"there is no such table with the {id}."
            }},
            status=status.HTTP_404_NOT_FOUND
        )
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == "DELETE":
        product.delete()
        return Response({
            "process": {
                "code": 204,
                "message": f"Product whose id was {id} has been deleted"
            }}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET', 'POST'])
def collection_list_api_view(request):
    if request.method == "GET":
        queryset = Collection.objects.annotate(
            product_count=Count('products')).all()
        serializer = CollectionSerializers(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CollectionSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST', 'DELETE'])
def collection_detail_api_views(request, id):
    collection = get_object_or_404(Collection.objects.annotate(
        product_count=Count('products')), pk=id)
    if request.method == 'GET':
        serializer = CollectionSerializers(collection)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializers(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({"error": "Collection cannot be deleted because it includes one or more  products."})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
