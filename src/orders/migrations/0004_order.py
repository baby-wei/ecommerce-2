# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0008_cart_tax_percentage'),
        ('orders', '0003_useraddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('billing_address', models.ForeignKey(related_name='billing_address', to='orders.UserCheckout')),
                ('cart', models.ForeignKey(to='carts.Cart')),
                ('user', models.ForeignKey(to='orders.UserCheckout')),
            ],
        ),
    ]
