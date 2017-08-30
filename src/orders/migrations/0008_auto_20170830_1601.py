# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_usercheckout_braintree_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=20, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(max_length=120, default='created', choices=[('created', 'Created'), ('paid', 'Paid'), ('shipped', 'Shipped')]),
        ),
    ]
