from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .api.serializers import ProductSerializer
from store.models import Product
from rest_framework import status


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