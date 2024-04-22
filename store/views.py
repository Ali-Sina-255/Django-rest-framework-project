from django.shortcuts import render, get_object_or_404
from django.db.models import Count
# searching, filtering, ordering
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

# serializer
from . filters import ProductFilter
from .api.serializers import ProductSerializer, CollectionSerializers, ReviewSerializers
from .models import OrderItem, Product, Collection, Review
# pagination
from rest_framework.pagination import PageNumberPagination
from .pagination import DefaultPagination
# ============================= ViewSets ========================


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # ============================= Filter with   DjangoFilterBackend  ========================
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id']
    # use custome filter class
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description', 'collection__title']
    ordering_fields = ['price', 'last_update']

    # ============================= filter with our logic ========================
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({"error": "Product cannot be deleted because it associated with an order items ."})
        product.delete()

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


class ProductDetailsApiView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # lookup_field = 'id'
    # when we use RetrieveUpdateDestroyAPIView inside this function is implemented get, put patch and delete just we overwrite the delete function
    # def get(self, request, id):
    #     product = get_object_or_404(Product, pk=id)
    #     serializer = ProductSerializer(product)
    #     return Response(serializer.data)

    # def put(self, request, id):
    #     product = get_object_or_404(Product, pk=id)
    #     serializer = ProductSerializer(instance=product, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({"error": "Product cannot be deleted because it associated with an order items ."})
        product.delete()


class CollectionListApiView(ListCreateAPIView):
    # one way
    queryset = Collection.objects.annotate(
        product_count=Count('products')).all()
    serializer_class = CollectionSerializers
    # an other way
    # def get_queryset(self):
    #     return  Collection.objects.annotate(product_count=Count('products')).all()

    # def get_serializer_class(self):
    #     return CollectionSerializers


class CollectionDetailsAPIView(RetrieveUpdateDestroyAPIView):
    queryset = collection = Collection.objects.annotate(
        product_count=Count('products'))
    serializer_class = CollectionSerializers

    # def get(self, request, id):
    #     collection = get_object_or_404(Collection.objects.annotate(
    #         product_count=Count('products')), pk=id)
    #     serializer = CollectionSerializers(collection)
    #     return Response(serializer.data)

    # def post(self, request, id):
    #     collection = get_object_or_404(Collection.objects.annotate(
    #         product_count=Count('products')), pk=id)
    #     serializer = CollectionSerializers(collection, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({"error": "Collection cannot be deleted because it includes one or more  products."})
        return super().destroy(request, *args, **kwargs)

    # def delete(self, request, pk):
    #     collection = get_object_or_404(Collection.objects.annotate(
    #         product_count=Count('products')), pk=pk)
    #     if collection.products.count() > 0:
    #         return Response({"error": "Collection cannot be deleted because it includes one or more  products."})
    #     collection.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


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


class ReviewViewSet(ModelViewSet):

    serializer_class = ReviewSerializers
    queryset = Review.objects.all()
    # def get_queryset(self):
    #     return Review.objects.filter(product_id= self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {"product_id": self.kwargs['product_pk']}


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
