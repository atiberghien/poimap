# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-02 15:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0023_customer_order_ticket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
