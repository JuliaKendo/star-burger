from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework import status
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
                {'error': 'Отсутствует информация о заказе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not (request.data.get('firstname') and isinstance(request.data['firstname'], str)):
            return Response(
                {'error': 'Не указано имя заказчика'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not (request.data.get('lastname') and isinstance(request.data['lastname'], str)):
            return Response(
                {'error': 'Не указана фамилия заказчика'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not (request.data.get('address') and isinstance(request.data['address'], str)):
            return Response(
                {'error': 'Не указан адрес заказа'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not (request.data.get('phonenumber') and isinstance(request.data['phonenumber'], str)):
            return Response(
                {'error': 'Не указан телефон заказчика'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not (request.data.get('products') and isinstance(request.data['products'], list)):
            return Response(
                {'error': 'В заказе отсутствуют продукты'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif [True for item in request.data['products'] if not item['product'] in Product.objects.values_list('id', flat=True)]:
            return Response(
                {'error': 'Заказан отсутствующий продукт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return handle_function(request)
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
