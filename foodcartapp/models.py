from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(
        ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='категория', related_name='products'
    )
    price = models.DecimalField(
        'цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField('картинка')
    special_status = models.BooleanField(
        'спец.предложение', default=False, db_index=True
    )
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE,
        related_name='menu_items', verbose_name="ресторан"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='menu_items', verbose_name='продукт'
    )
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def fetch_orders_with_price(self):
        return self.annotate(Sum('order_products__cost'))


class Order(models.Model):
    registred_at = models.DateTimeField(
        'Дата создания', default=timezone.now, db_index=True
    )
    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50)
    address = models.CharField('адрес', max_length=100, db_index=True)
    phonenumber = PhoneNumberField('телефон заказчика', db_index=True)
    status_order = models.CharField(
        'статус обработки', max_length=10, default='raw', choices=(
            ('raw', 'Необработанный'),
            ('processed', 'Обработанный')
        ), db_index=True)
    payment_type = models.CharField(
        'Форма оплаты', max_length=10, default='cash', choices=(
            ('cash', 'Наличные, при получении'),
            ('online', 'Предоплата онлайн')
        ), db_index=True)
    called_at = models.DateTimeField(
        'Дата созвона', blank=True, null=True, db_index=True
    )
    delivered_at = models.DateTimeField(
        'Дата доставки', blank=True, null=True, db_index=True
    )
    comment = models.TextField('комментарий', max_length=200, blank=True)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL,
        related_name='orders', verbose_name="ресторан", null=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='order_products', verbose_name="заказ"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='product_by_orders', verbose_name='продукт'
    )
    quantity = models.PositiveIntegerField('количество')
    cost = models.DecimalField(
        'стоимость', max_digits=8, decimal_places=2,
        default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product} {self.order}'
