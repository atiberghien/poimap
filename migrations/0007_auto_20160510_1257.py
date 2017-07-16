# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0006_auto_20160510_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arret',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='arret',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
