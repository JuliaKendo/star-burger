# Generated by Django 3.0.7 on 2021-07-30 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_auto_20210730_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_items', to='foodcartapp.Product', verbose_name='продукт'),
        ),
    ]
