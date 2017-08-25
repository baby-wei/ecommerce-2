# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_productfeatured_text_css_color'),
        ('carts', '0002_auto_20170825_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(to='products.Variation', through='carts.CartItem'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(default=1, to='carts.Cart'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cartitem',
            name='item',
            field=models.ForeignKey(default=1, to='products.Variation'),
            preserve_default=False,
        ),
    ]
