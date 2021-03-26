from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum, FloatField


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
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderQuerySet(models.QuerySet):

    def fetch_orders_with_price(self):
        return ProductsOrdered.objects.order_by('order').values(
            'order',
            address=F('order__address'),
            firstname=F('order__firstname'),
            lastname=F('order__lastname'),
            phonenumber=F('order__phonenumber')
        ).annotate(
            total_price=Sum(F('product__price') * F('quantity'), output_field=FloatField())
        )


class Order(models.Model):
    address = models.CharField('адрес', max_length=100)
    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50)
    phonenumber = PhoneNumberField('телефон заказчика')

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'

    class Meta:
        ordering = ['id']
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class ProductsOrdered(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='oders', verbose_name="заказ"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='oder_items', verbose_name='продукт'
    )
    quantity = models.PositiveIntegerField('количество')

    def __str__(self):
        return f'{self.product} {self.order}'

    class Meta:
        ordering = ['id']
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
