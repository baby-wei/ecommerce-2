# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_total',
            field=models.DecimalField(default=0.0, max_digits=50, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(null=True, related_name='shipping_address', to='orders.UserAddress'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_total_price',
            field=models.DecimalField(default=5.99, max_digits=50, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(null=True, related_name='billing_address', to='orders.UserAddress'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, to='orders.UserCheckout'),
        ),
    ]
