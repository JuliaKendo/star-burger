import pdb
from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, ProductsOrdered


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


def validate_json(handle_function):
    def inner(request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'Отсутствует информация о заказе'}, headers={'Accept': 'json'}
            )
        elif not ('products' in request.data.keys() and request.data['products']):
            return Response(
                {'error': 'В заказе отсутствуют продукты'}, headers={'Accept': 'json'}
            )
        elif not isinstance(request.data['products'], list):
            return Response(
                {'error': 'Отсутствует информация о продуктах'}, headers={'Accept': 'json'}
            )
        handle_function(request)
    return inner


@api_view(['POST'])
@validate_json
def register_order(request):
    order = Order.objects.create(
        **{key: value for key, value in request.data.items() if key != 'products'}
    )
    for row_of_order in request.data['products']:
        product = get_object_or_404(Product, id=row_of_order['product'])
        ProductsOrdered.objects.create(
            order=order, product=product, quantity=row_of_order['quantity']
        )

    return Response({}, headers={'Accept': 'json'})
