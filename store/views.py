from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .api.serializers import ProductSerializer, CollectionSerializers
from store.models import Product, Collection
from rest_framework import status
from django.db.models import Count
from rest_framework.views import APIView

from rest_framework.generics  import ListCreateAPIView
 
# ============================= ListCreateAPIView ========================


class ProductListApiView(ListCreateAPIView):
    # if have no any special logic should use this tow method
    # get_queryset = Product.objects.select_related('collection').all()
    # get_serializer_class = ProductSerializer
    
    def get_queryset(self):
        return Product.objects.select_related('collection').all()
    
    def get_serializer_class(self):
        return ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}
    

class ProductDetailsApiView(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        product.delete()

class CollectionListApiView(ListCreateAPIView):
    # one way 
    queryset = Collection.objects.annotate(product_count=Count('products')).all()
    serializer_class = CollectionSerializers
    # an other way
    # def get_queryset(self):
    #     return  Collection.objects.annotate(product_count=Count('products')).all()
    
    # def get_serializer_class(self):
    #     return CollectionSerializers



class CollectionDetailsAPIView(APIView):
    def get(self, request, id):
        collection = get_object_or_404(Collection.objects.annotate(
            product_count=Count('products')), pk=id)
        serializer = CollectionSerializers(collection)
        return Response(serializer.data)

    def post(self, request, id):
        collection = get_object_or_404(Collection.objects.annotate(
            product_count=Count('products')), pk=id)
        serializer = CollectionSerializers(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        collection = get_object_or_404(Collection.objects.annotate(
            product_count=Count('products')), pk=id)
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
