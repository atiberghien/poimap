# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-20 11:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0016_auto_20180404_1611'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RunningDay',
        ),
    ]
