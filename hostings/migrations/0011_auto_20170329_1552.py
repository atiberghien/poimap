# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 13:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hostings', '0010_auto_20170329_1316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hostings',
            name='address',
        ),
        migrations.RemoveField(
            model_name='hostings',
            name='city',
        ),
        migrations.RemoveField(
            model_name='hostings',
            name='geom',
        ),
        migrations.RemoveField(
            model_name='hostings',
            name='zipcode',
        ),
    ]
