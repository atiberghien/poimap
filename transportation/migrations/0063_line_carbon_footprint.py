# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-07 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0062_auto_20200504_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='carbon_footprint',
            field=models.CharField(default='0', max_length=40),
        ),
    ]