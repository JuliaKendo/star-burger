# Generated by Django 3.0.7 on 2021-08-09 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_auto_20210730_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('cash', 'Наличные, при получении'), ('online', 'Предоплата онлайн')], db_index=True, max_length=10, null=True, verbose_name='Форма оплаты'),
        ),
    ]
