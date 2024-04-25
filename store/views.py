from django.shortcuts import render, get_object_or_404
from django.db.models import Count
# searching, filtering, ordering
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions

# serializer
from .filters import ProductFilter
from .api.serializers import (ProductSerializer,
                              CollectionSerializers,
                              ReviewSerializers,
                              CartSerializers,
                              CartItemSerializers,
                              AddCartItemSerializer,
                              UpdateCartItemSerializer
                              )
from store.api.customerSerializer import CustomerSerializer
from .models import OrderItem, Product, Collection, Review, Cart, CartItem, Customer
# pagination
from rest_framework.pagination import PageNumberPagination
from .pagination import DefaultPagination
from .permissions import FullDjangoModelPermission, IsAdminOrReadyOnly, ViewCustomerHistoryPermissions


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
    permission_classes = [IsAdminOrReadyOnly]

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
    permission_classes = [IsAdminOrReadyOnly]
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
    permission_classes = [IsAdminOrReadyOnly]

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


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializers


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        else:
            return CartItemSerializers

    def get_serializer_context(self):
        return {"cart_id": self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermissions])
    def history(self, request, pkd):
        return Response('OK')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
