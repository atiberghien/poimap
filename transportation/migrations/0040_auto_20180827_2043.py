# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-27 20:43
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0039_auto_20180821_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='name', unique=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='name', unique=True),
        ),
    ]
