from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from collections import Counter
from more_itertools import first

from restaurateur.geo import calculate_distance
from foodcartapp.models import (
    Product, Restaurant,
    RestaurantMenuItem, Order,
    ProductsOrdered,
    CoordinatesAddresses
)


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def allocate_restaurants_on_order(order, products, restaurants):
    products_in_order = [
        item['product'] for item in products if item['order'] == order.id
    ]
    restaurants_by_order = Counter(
        (
            items['restaurant__name'], items['restaurant__address']
        ) for items in restaurants if items['product'] in products_in_order
    )
    return [
        first(item) for item in restaurants_by_order.most_common(len(products_in_order))
    ]


def get_locations(orders, restaurants):
    locations = []
    if restaurants:
        locations.extend(
            CoordinatesAddresses.objects.get_coordinates(
                restaurants.values_list('restaurant__address')
            ).values()
        )
    if orders:
        locations.extend(
            CoordinatesAddresses.objects.get_coordinates(
                orders.values_list('address')
            ).values()
        )
    return locations


def fetch_coordinates(address, coordinates):
    try:
        found_coordinates = next(
            filter(lambda item: item['address'] == address, coordinates)
        )
    except (StopIteration, TypeError):
        return 0, 0
    return found_coordinates['lng'], found_coordinates['lat']


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.fetch_orders_with_price()
    products = ProductsOrdered.objects.filter(
        order__in=orders
    ).values('order', 'product')
    restaurants = RestaurantMenuItem.objects.filter(
        availability=True, product__in=products.values('product')
    ).values('restaurant__name', 'restaurant__address', 'product')
    locations = get_locations(orders, restaurants)
    orders_info = []
    for order in orders:
        order_info = {'restaurants': []}
        order_info['order'] = order
        order_info['status'] = order.get_status_order_display()
        order_info['payment'] = order.get_payment_type_display()
        coordinates_from = fetch_coordinates(order.address, locations)
        for restaurant_info in allocate_restaurants_on_order(order, products, restaurants):
            name, address = restaurant_info
            order_info['restaurants'].append(
                {
                    'name': name,
                    'distance': calculate_distance(
                        coordinates_from,
                        fetch_coordinates(address, locations)
                    )
                }
            )
        order_info['restaurants'] = sorted(
            order_info['restaurants'], key=lambda x: x['distance']
        )
        orders_info.append(order_info)
    return render(request, template_name='order_items.html', context={
        'order_items': orders_info,
    })
