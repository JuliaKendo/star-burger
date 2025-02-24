from django.contrib import admin
from django.conf import settings
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme


from .models import (
    Product,
    ProductCategory,
    Restaurant,
    RestaurantMenuItem,
    Order,
    OrderItem
)
from addressclassifier.models import CoordinatesAddresses
from addressclassifier.addressclassifier_lib import save_address


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'cost')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def response_post_save_change(self, request, obj):
        if not CoordinatesAddresses.objects.get_coordinates([obj.address]).exists():
            save_address(obj.address)
        return super().response_post_save_change(request, obj)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" height="200"/>', url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" height="50"/></a>',
            edit_url=edit_url, src=obj.image.url
        )
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInLine]
    readonly_fields = ('registred_at',)
    list_display = [
        'id',
        'registred_at',
        'firstname',
        'lastname',
        'address',
        'phonenumber',
        'status_order',
        'payment_type',
        'comment'
    ]
    fields = (
        'registred_at',
        ('status_order', 'payment_type'),
        ('firstname', 'lastname'),
        ('phonenumber', 'address'),
        ('called_at', 'delivered_at'),
        'restaurant',
        'comment'
    )

    def response_post_save_change(self, request, obj):
        if "next" in request.GET and url_has_allowed_host_and_scheme(
            request.GET['next'], settings.ALLOWED_HOSTS
        ):
            return redirect(request.GET['next'])
        if not CoordinatesAddresses.objects.get_coordinates([obj.address]).exists():
            save_address(obj.address)
        return super().response_post_save_change(request, obj)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product', 'quantity', 'cost',
    ]
    raw_id_fields = ['order', 'product']
