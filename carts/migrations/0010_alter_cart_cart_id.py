# Generated by Django 4.2.4 on 2023-11-16 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0009_alter_cart_cart_id_alter_cartitem_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(max_length=240, null=True),
        ),
    ]
