# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-24 14:01
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0032_auto_20180618_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='equipments',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
