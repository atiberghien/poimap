# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 08:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poimap', '0012_auto_20170403_1259'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='base',
        #     name='media',
        # ),
        migrations.DeleteModel(
            name='Base',
        ),
    ]
