# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-03 17:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0046_auto_20190303_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]
