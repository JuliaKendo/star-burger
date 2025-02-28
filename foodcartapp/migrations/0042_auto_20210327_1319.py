# Generated by Django 3.0.7 on 2021-03-27 13:19

import django.core.validators
from django.db import migrations, models
from django.db.models import F, Sum, DecimalField


def fill_prod_cost_in_orders(apps, shema_editor):
    ProductsOrdered = apps.get_model('foodcartapp', 'OrderItem')
    product_with_costs = ProductsOrdered.objects.annotate(
        new_cost=Sum(F('product__price') * F('quantity'), output_field=DecimalField())
    )
    for row in product_with_costs:
        row.cost = row.new_cost
    ProductsOrdered.objects.bulk_update(product_with_costs, ['cost'])


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20210324_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='количество'),
        ),
        migrations.RunPython(fill_prod_cost_in_orders),
    ]
