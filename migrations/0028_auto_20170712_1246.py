# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-12 12:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poimap', '0031_auto_20170605_2155'),
        ('transportation', '0027_auto_20170712_1223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stop',
            name='id',
        ),
        migrations.RemoveField(
            model_name='stop',
            name='poi_id',
        ),
        migrations.AddField(
            model_name='stop',
            name='poi_ptr',
            field=models.OneToOneField(auto_created=True, default=0, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='poimap.POI'),
            preserve_default=False,
        ),
    ]
