from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import (
    Product, Order, OrderItem
)
from addressclassifier.models import CoordinatesAddresses
from restaurateur.geo import fetch_coordinates


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True, write_only=True, allow_empty=False
    )

    class Meta:
        model = Order
        fields = [
            'firstname', 'lastname',
            'address', 'phonenumber',
            'products',
        ]


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):

    def calc_cost(row_of_order):
        product = row_of_order['product']
        return product.price * Decimal(row_of_order['quantity'])

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        order = Order.objects.create(
            **{key: value for key, value in serializer.validated_data.items() if key != 'products'}
        )

        ordered_products = serializer.validated_data['products']
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order, cost=calc_cost(fields), **fields
            ) for fields in ordered_products
        ])

    address = serializer.validated_data['address']
    lng, lat = fetch_coordinates(
        settings.YANDEX_API_KEY, address
    )
    if lng and lat:
        CoordinatesAddresses.objects.update_or_create(
            address=address,
            defaults={
                'address': address,
                'lng': lng, 'lat': lat
            }
        )

    return Response(OrderSerializer(order).data)
