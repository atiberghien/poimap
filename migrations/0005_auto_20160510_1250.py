# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0004_auto_20160510_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arret',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=44.523238, max_digits=10),
        ),
        migrations.AlterField(
            model_name='arret',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=3.477935, max_digits=10),
        ),
    ]
