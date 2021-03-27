from decimal import Decimal
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import Product, Order, ProductsOrdered


class ProductsOrderedSerializer(ModelSerializer):

    class Meta:
        model = ProductsOrdered
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ProductsOrderedSerializer(many=True, write_only=True, allow_empty=False)

    class Meta:
        model = Order
        fields = '__all__'


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

    order = Order.objects.create(
        **{key: value for key, value in serializer.validated_data.items() if key != 'products'}
    )
    order_fields = serializer.validated_data['products']
    products = [ProductsOrdered(order=order, cost=calc_cost(fields), **fields) for fields in order_fields]
    ProductsOrdered.objects.bulk_create(products)
    return Response(OrderSerializer(order).data)
