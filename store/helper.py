 
from . models import Product, Collection
from store.api.serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.decorators import APIView
# ============================= ListCreateAPIView ========================


 
# ============================= Class base view ========================
class ProductListApiView(APIView):
    def get(self, request):
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



# class CollectionListApiView(APIView):
#     def get(self, request):
#         queryset = Collection.objects.annotate(
#             product_count=Count('products')).all()
#         serializer = CollectionSerializers(queryset, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = CollectionSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
