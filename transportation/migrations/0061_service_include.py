# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-05-04 07:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0060_auto_20200123_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='include',
            field=models.BooleanField(default=True),
        ),
    ]
